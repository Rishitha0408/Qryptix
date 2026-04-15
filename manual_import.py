from app import app, db, VerificationSource
import openpyxl
import os

def import_excel():
    with app.app_context():
        file_path = "dummy_doctors_updated (2).xlsx"
        if not os.path.exists(file_path):
            print("Excel file not found.")
            return
            
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        headers = [cell.value for cell in sheet[1]]
        
        imported = 0
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data = dict(zip(headers, row))
            doc_id = str(data.get('Doctor ID', '')).strip()
            if not doc_id: continue
            
            if not VerificationSource.query.filter_by(doctor_id=doc_id).first():
                new_entry = VerificationSource(
                    doctor_id=doc_id,
                    doctor_name=data.get('Doctor Name'),
                    registration_year=str(data.get('Year of Registration')),
                    mobile_number=str(data.get('SMC Mobile Number')),
                    email=data.get('Email'),
                    state=data.get('State')
                )
                db.session.add(new_entry)
                imported += 1
        
        db.session.commit()
        print(f"Imported {imported} records.")

if __name__ == "__main__":
    import_excel()
