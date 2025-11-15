import sys
import mysql.connector 
from PyQt6.uic import loadUi
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',                        
    'password': 'group2s14',     
    'database': 'pet_show'          
}
#YEYE
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"MySQL Connection Error: {err}")
        return None
#--------------------------------------------------------------------------------------------------------------------

class RegisterScreen(QDialog):
    def __init__(self):
        super(RegisterScreen, self).__init__()
        loadUi('./gui/registerscreen.ui', self)
        self.regbutt.clicked.connect(self.gotoownerregistration)

    def gotoownerregistration(self):
        ownerreg = OwnerRegisScreen()
        widget.addWidget(ownerreg)
        widget.setCurrentIndex(widget.currentIndex() + 1)

#--------------------------------------------------------------------------------------------------------------------

class OwnerRegisScreen(QDialog):
    def __init__(self):
        super(OwnerRegisScreen, self).__init__()
        loadUi('./gui/ownerregistration.ui', self)
        self.owregbutt.clicked.connect(self.registerfunc)
        
    def registerfunc(self):
        userfirstname = self.owfirstname.text().strip()
        userlastname = self.owlastname.text().strip()
        useremail = self.owemail.text().strip()
        usernumber = self.ownumber.text().strip()
        

        if (len(userfirstname) == 0 or len(userlastname) == 0):
            self.owerrormes.setText('Please fill in all required fields.')
            
        else:
            conn = get_db_connection()
            
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # Get the next available owner_id (since your table is not AUTO_INCREMENT)
                    cursor.execute("SELECT MAX(owner_id) FROM owners")
                    max_id = cursor.fetchone()[0]
                    new_owner_id = (max_id if max_id is not None else 0) + 1
                    
                    sql = "INSERT INTO owners (owner_id, first_name, last_name, email, contact_number) VALUES (%s, %s, %s, %s, %s)"
                    data = (new_owner_id, userfirstname, userlastname, useremail, usernumber)
                    
                    cursor.execute(sql, data)
                    conn.commit()
                    self.gotommenu()

                except mysql.connector.Error as err:
                    print(f"Database INSERT Error: {err}")
                    self.owerrormes.setText(f'Registration failed: DB Error.')
                except Exception as e:
                    print(f"Unexpected Error during registration: {e}")
                    self.owerrormes.setText('An unexpected error occurred.')
                finally:
                    # 4. Always close the connection
                    if conn.is_connected():
                        conn.close()
            else:
                # 3. Handle connection failure
                self.owerrormes.setText('Database connection failed. Check credentials/server.')

            self.gotommenu()

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)
      
#--------------------------------------------------------------------------------------------------------------------

class mainmenu(QDialog):
    def __init__(self):
        super(mainmenu, self).__init__()
        loadUi('./gui/mainmenu.ui', self)
        self.petregbutt.clicked.connect(self.gotopetregis)
        self.petregbutt.clicked.connect(self.gotopetregis)
        self.eventregbutt.clicked.connect(self.gotoenrollev)
        self.editinbutt.clicked.connect(self.gotoeditinfo)
        self.mmexitbutt.clicked.connect(self.quit_application)

    def quit_application(self):
        app.quit()

    def gotopetregis(self):
        petregis = petregistration()
        widget.addWidget(petregis)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoenrollev(self):
        enrollev = enrollevent()
        widget.addWidget(enrollev)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoeditinfo(self):
        editin = editinf()
        widget.addWidget(editin)
        widget.setCurrentIndex(widget.currentIndex() + 1)

#--------------------------------------------------------------------------------------------------------------------

class petregistration(QDialog):
    def __init__(self):
        super(petregistration, self).__init__()
        loadUi('./gui/petregistration.ui', self)

        self.petsex.addItems(['Male', 'Female', 'Unknown'])
        self.petsize.addItems(['Small', 'Medium', 'Large', 'Extra Large'])

        self.petexitbutt.clicked.connect(self.gotommenu)
        self.petregisterbutt.clicked.connect(self.petregisfunc)
        
    def petregisfunc(self):
        petname = self.petname.text().strip()
        petage = self.petage.value()
        petsex = self.petsex.currentText().strip()
        petweight = self.petweight.value()
        petsize_name = self.petsize.currentText().strip()
        petbreed = self.petbreed.text().strip()
        petnotes = self.petnotes.toPlainText().strip()

        self.petregiserr.setText('') 

        if not petname or petage == 0 or not petbreed:
            self.petregiserr.setText('Please fill in Pet Name, Age (must be > 0), and Breed.')
            return
        
        muzzle_required = 1 if self.muzzleyes.isChecked() else 0 
        
        size_map = {'Small': 1, 'Medium': 2, 'Large': 3, 'Extra Large': 3}
        actual_size_id = size_map.get(petsize_name, 3)

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute("SELECT MAX(owner_id) FROM owners")
                current_owner_id = cursor.fetchone()[0]
                
                if current_owner_id is None:
                    self.petregiserr.setText('Error: No owner found. Please register an owner first.')
                    return

                cursor.execute("SELECT MAX(pet_id) FROM pets")
                max_pet_id = cursor.fetchone()[0]
                new_pet_id = (max_pet_id if max_pet_id is not None else 0) + 1
                
                sql_breed_lookup = "SELECT breed_id FROM breeds WHERE breed_name = %s"
                cursor.execute(sql_breed_lookup, (petbreed,))
                breed_result = cursor.fetchone()

                if not breed_result:
                    self.petregiserr.setText(f"Breed '{petbreed}' not found in the database. Please check spelling.")
                    return
                
                breed_id = breed_result[0]
                
                sql_pet = """
                INSERT INTO pets 
                (pet_id, owner_id, name, actual_size_id, age, sex, weight_kg, muzzle_required, notes) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data_pet = (
                    new_pet_id, 
                    current_owner_id, 
                    petname, 
                    actual_size_id, 
                    petage, 
                    petsex, 
                    petweight, 
                    muzzle_required, 
                    petnotes
                )
                
                cursor.execute(sql_pet, data_pet)

                sql_junction = "INSERT INTO pet_breed_junction (pet_id, breed_id) VALUES (%s, %s)"
                data_junction = (new_pet_id, breed_id)
                
                cursor.execute(sql_junction, data_junction)
                
                conn.commit()
                
                self.gotopetregistered()
                
            except mysql.connector.Error as err:
                print(f"Database INSERT Error: {err}")
                self.petregiserr.setText(f'Registration failed: DB Error.')
            except Exception as e:
                print(f"Unexpected Error during pet registration: {e}")
                self.petregiserr.setText('An unexpected error occurred.')
            finally:
                if conn.is_connected():
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')

    def gotopetregistered(self):
        pregistrd = petrgistrd()
        widget.addWidget(pregistrd)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

#--------------------------------------------------------------------------------------------------------------------

class petrgistrd(QDialog):
    def __init__(self):
        super(petrgistrd, self).__init__()
        loadUi('./gui/petregistered!.ui', self)
        self.sucpetregbackbutt.clicked.connect(self.gotommenu)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)
       
#--------------------------------------------------------------------------------------------------------------------

class enrollevent(QDialog):
    def __init__(self):
        super(enrollevent, self).__init__()
        loadUi('./gui/enrollevent.ui', self)
        self.enrollevexitbutt.clicked.connect(self.gotommenu)
        self.enrolevbutt.clicked.connect(self.gotoeventenroll)
    def enrollevnt(self):
        # petname = self.petname.text()
        # # petage = self.petage.text()
        # # petsex = self.petname.text()
        # # petweight = self.petweight.text()
        # # petmuzzle = self.petname.text()
        # # petsize = self.petname.text()
        # # petbreed = self.petbreed.text()
        # # petnotes = self.petnotes.text()

        # if (len(petname) == 0):
        #     self.petregiserr.setText('Please fill in all required fields.')
        
        # else:
        self.gotopetregistered()

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoeventenroll(self):
        eventrolled = evenrolled()
        widget.addWidget(eventrolled)
        widget.setCurrentIndex(widget.currentIndex() + 1)
       
#--------------------------------------------------------------------------------------------------------------------

class evenrolled(QDialog):
    def __init__(self):
        super(evenrolled, self).__init__()
        loadUi('./gui/eventenrolled.ui', self)
        self.eventenrolledbutt.clicked.connect(self.gotommenu)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

#--------------------------------------------------------------------------------------------------------------------

class editinf(QDialog):
    def __init__(self):
        super(editinf, self).__init__()
        loadUi('./gui/editinfo.ui', self)
        self.editexitbutt.clicked.connect(self.gotommenu)
        self.saveinfobutt.clicked.connect(self.gotoinfoedited)
    def saveinf(self):
        # petname = self.petname.text()
        # # petage = self.petage.text()
        # # petsex = self.petname.text()
        # # petweight = self.petweight.text()
        # # petmuzzle = self.petname.text()
        # # petsize = self.petname.text()
        # # petbreed = self.petbreed.text()
        # # petnotes = self.petnotes.text()

        # if (len(petname) == 0):
        #     self.petregiserr.setText('Please fill in all required fields.')
        
        # else:
        self.gotoinfoedited()

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoinfoedited(self):   
        infoedtd = infoedited()
        widget.addWidget(infoedtd)
        widget.setCurrentIndex(widget.currentIndex() + 1)
       
#--------------------------------------------------------------------------------------------------------------------

class infoedited(QDialog):
    def __init__(self):
        super(infoedited, self).__init__()
        loadUi('./gui/infoedited!.ui', self)
        self.infoeditedbackbutt.clicked.connect(self.gotommenu)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

#--------------------------------------------------------------------------------------------------------------------

#main
app = QApplication(sys.argv)
registerscreen = RegisterScreen()
widget = QStackedWidget()

widget.addWidget(registerscreen)
widget.setFixedHeight(526)
widget.setFixedWidth(808)
widget.show()

try:
    sys.exit(app.exec())
except:
    print('Exiting')