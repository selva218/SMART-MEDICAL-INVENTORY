from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from config import Config
from models import db, Medicine
from forms import MedicineForm
from utils import check_expired_and_near_expiry, check_low_stock
from datetime import datetime
import os, csv, io, pandas as pd

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        expiry = check_expired_and_near_expiry(30)
        low = check_low_stock()
        return render_template('index.html', expiry=expiry, low=low)

    @app.route('/inventory')
    def inventory():
        q = request.args.get('q', '').strip()
        meds = Medicine.query
        if q:
            meds = meds.filter(Medicine.name.ilike(f'%{q}%'))
        meds = meds.order_by(Medicine.name).all()
        return render_template('inventory.html', meds=meds, q=q)

    @app.route('/medicine/add', methods=['GET','POST'])
    def add_medicine():
        form = MedicineForm()
        if form.validate_on_submit():
            med = Medicine(
                name=form.name.data.strip(),
                batch=form.batch.data.strip() if form.batch.data else None,
                quantity=form.quantity.data,
                unit=form.unit.data or 'pcs',
                expiry_date=form.expiry_date.data,
                threshold=form.threshold.data or 5,
                notes=form.notes.data
            )
            db.session.add(med)
            db.session.commit()
            flash('Medicine added.','success')
            return redirect(url_for('inventory'))
        return render_template('add_edit_medicine.html', form=form, action='Add')

    @app.route('/medicine/<int:med_id>/edit', methods=['GET','POST'])
    def edit_medicine(med_id):
        med = Medicine.query.get_or_404(med_id)
        form = MedicineForm(obj=med)
        if form.validate_on_submit():
            med.name = form.name.data.strip()
            med.batch = form.batch.data.strip() if form.batch.data else None
            med.quantity = form.quantity.data
            med.unit = form.unit.data or 'pcs'
            med.expiry_date = form.expiry_date.data
            med.threshold = form.threshold.data or med.threshold
            med.notes = form.notes.data
            db.session.commit()
            flash('Updated.','success')
            return redirect(url_for('inventory'))
        return render_template('add_edit_medicine.html', form=form, action='Edit')

    @app.route('/medicine/<int:med_id>/delete', methods=['POST'])
    def delete_medicine(med_id):
        med = Medicine.query.get_or_404(med_id)
        db.session.delete(med)
        db.session.commit()
        flash('Deleted.','info')
        return redirect(url_for('inventory'))

    @app.route('/alerts')
    def alerts():
        expiry = check_expired_and_near_expiry(30)
        low = check_low_stock()
        return render_template('alerts.html', expiry=expiry, low=low)

    @app.route('/upload', methods=['GET','POST'])
    def upload():
        if request.method=='POST':
            file = request.files.get('file')
            if not file:
                flash('No file','danger')
                return redirect(url_for('upload'))
            try:
                import pandas as pd
                df = pd.read_csv(file)
            except Exception as e:
                flash(f'CSV error: {e}','danger')
                return redirect(url_for('upload'))

            added=0
            for _,row in df.iterrows():
                name = str(row.get('name') or '').strip()
                if not name: continue
                batch = row.get('batch')
                qty = int(row.get('quantity') or 0)
                unit = row.get('unit') or 'pcs'
                expiry_raw = row.get('expiry_date')
                expiry = None
                if pd.notna(expiry_raw):
                    try:
                        expiry = pd.to_datetime(expiry_raw).date()
                    except:
                        expiry=None
                threshold = int(row.get('threshold') or 5)
                notes = row.get('notes')

                med = Medicine(
                    name=name, batch=batch,
                    quantity=qty, unit=unit,
                    expiry_date=expiry,
                    threshold=threshold, notes=notes
                )
                db.session.add(med)
                added+=1
            db.session.commit()
            flash(f'Imported {added} items.','success')
            return redirect(url_for('inventory'))
        return render_template('upload.html')

    @app.route('/export')
    def export_csv():
        meds = Medicine.query.order_by(Medicine.name).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id','name','batch','quantity','unit','expiry_date','threshold','notes'])
        for m in meds:
            writer.writerow([
                m.id, m.name, m.batch or '', m.quantity,
                m.unit, m.expiry_date or '', m.threshold, m.notes or ''
            ])
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='medicines.csv'
        )

    return app

if __name__=='__main__':
    app=create_app()
    app.run(debug=True)
