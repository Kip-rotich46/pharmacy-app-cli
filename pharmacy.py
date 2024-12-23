import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

# Database setup (change the URL as per your configuration)
DATABASE_URL = "sqlite:///pharmacy.db"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(50))  # e.g., 'pharmacist', 'staff'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Drug(Base):
    __tablename__ = 'drugs'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(String(255))

    def __repr__(self):
        return f"<Drug(name={self.name}, price={self.price}, quantity={self.quantity})>"


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    drug_id = Column(Integer, ForeignKey('drugs.id'))
    quantity_sold = Column(Integer)
    total_price = Column(Float)
    date = Column(Date)

    drug = relationship('Drug')


# User Authentication Functions
def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    role = input("Enter role (e.g., pharmacist, staff): ")

    # Check if user already exists
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        print("User already exists!")
        return

    # Create new user and hash password
    new_user = User(username=username, role=role)
    new_user.set_password(password)

    # Add user to the database
    session.add(new_user)
    session.commit()
    print(f"User {username} registered successfully!")


def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Check if the user exists
    user = session.query(User).filter_by(username=username).first()
    if user and user.check_password(password):
        print(f"Welcome back, {username}!")
    else:
        print("Invalid username or password!")


# Inventory Management Functions
def add_drug():
    name = input("Enter drug name: ")
    price = float(input("Enter drug price: "))
    quantity = int(input("Enter drug quantity: "))
    description = input("Enter drug description: ")

    # Create new drug
    new_drug = Drug(name=name, price=price, quantity=quantity, description=description)

    # Add to the database
    session.add(new_drug)
    session.commit()
    print(f"Drug {name} added successfully!")


def update_drug():
    drug_name = input("Enter drug name to update: ")
    drug = session.query(Drug).filter_by(name=drug_name).first()

    if drug:
        name = input(f"Enter new name (current: {drug.name}): ") or drug.name
        price = float(input(f"Enter new price (current: {drug.price}): ") or drug.price)
        quantity = int(input(f"Enter new quantity (current: {drug.quantity}): ") or drug.quantity)
        description = input(f"Enter new description (current: {drug.description}): ") or drug.description

        drug.name = name
        drug.price = price
        drug.quantity = quantity
        drug.description = description

        # Commit the changes
        session.commit()
        print(f"Drug {name} updated successfully!")
    else:
        print("Drug not found!")

def delete_drug():
    drug_id = int(input("Enter drug ID to delete: "))
    drug = session.query(Drug).filter_by(id=drug_id).first()

    if drug:
        session.delete(drug)
        session.commit()
        print(f"Drug {drug.name} deleted successfully!")
    else:
        print("Drug not found!")


# POS Transaction Functions
def sell_drug():
    drug_name = input("Enter drug name: ")
    quantity = int(input("Enter quantity to sell: "))

    # Query drug by name
    drug = session.query(Drug).filter(Drug.name == drug_name).first()

    if drug and drug.quantity >= quantity:
        total_price = drug.price * quantity
        drug.quantity -= quantity

        # Create a sale record
        new_sale = Sale(drug_id=drug.id, quantity_sold=quantity, total_price=total_price, date=datetime.date.today())
        session.add(new_sale)
        session.commit()

        # Print receipt
        print(f"Sale completed! Drug: {drug_name} | Quantity: {quantity} | Total Price: {total_price}")
        print("Receipt: Sale recorded successfully!")
    else:
        print("Not enough stock!")


# Report Generation Functions
def generate_daily_sales_report():
    today = datetime.date.today()
    sales_data = session.query(Sale, Drug.name).join(Drug, Sale.drug_id == Drug.id).filter(Sale.date == today).all()

    if sales_data:
        total_sales = 0
        print(f"Sales Report for {today}:")
        for sale, drug_name in sales_data:
            print(f"Drug: {drug_name} | Quantity Sold: {sale.quantity_sold} | Total Price: {sale.total_price}")
            total_sales += sale.total_price
        print(f"\nTotal sales today: {total_sales}")
    else:
        print("No sales data found for today.")


def generate_stock_report():
    drugs = session.query(Drug).all()

    if drugs:
        print("Current Stock Levels:")
        for drug in drugs:
            print(f"Drug: {drug.name} | Quantity: {drug.quantity}")
    else:
        print("No drugs in inventory.")


def generate_order_history_report():
    sales_data = session.query(Sale, Drug.name).join(Drug, Sale.drug_id == Drug.id).all()

    if sales_data:
        print("Order History Report:")
        for sale, drug_name in sales_data:
            print(f"Drug: {drug_name} | Quantity Sold: {sale.quantity_sold} | Total Price: {sale.total_price} | Date: {sale.date}")
    else:
        print("No order history found.")


# Main Menu Function
def main():
    while True:
        print("\nPharmacy System Menu:")
        print("1. Register User")
        print("2. Login User")
        print("3. Add Drug")
        print("4. Update Drug")
        print("5. Delete Drug")
        print("6. Sell Drug")
        print("7. Generate Daily Sales Report")
        print("8. Generate Stock Report")
        print("9. Generate Order History Report")
        print("10. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            add_drug()
        elif choice == '4':
            update_drug()
        elif choice == '5':
            delete_drug()
        elif choice == '6':
            sell_drug()
        elif choice == '7':
            generate_daily_sales_report()
        elif choice == '8':
            generate_stock_report()
        elif choice == '9':
            generate_order_history_report()
        elif choice == '10':
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == '__main__':
    Base.metadata.create_all(engine)  # Create tables
    main()
