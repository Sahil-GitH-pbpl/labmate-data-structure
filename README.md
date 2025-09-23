# lab
labxs.11
# Doctor class
class Doctor:
    def __init__(self, doctor_id, name, specialty):
        self.doctor_id = doctor_id
        self.name = name
        self.specialty = specialty

# Patient class
class Patient:
    def __init__(self, patient_id, name, age, doctor_id):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.doctor_id = doctor_id

# Example data
doctors = [
    Doctor(1, "Dr. Smith", "Cardiology"),
    Doctor(2, "Dr. Jones", "Neurology")
]

patients = [
    Patient(101, "Alice", 30, 1),
    Patient(102, "Bob", 45, 2)
]

# Display all doctors
print("Doctors:")
for doc in doctors:
    print(f"ID: {doc.doctor_id}, Name: {doc.name}, Specialty: {doc.specialty}")

# Display all patients
print("\nPatients:")
for pat in patients:
    print(f"ID: {pat.patient_id}, Name: {pat.name}, Age: {pat.age}, Doctor ID: {pat.doctor_id}")
