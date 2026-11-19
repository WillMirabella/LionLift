import db

class Car:
    def __init__(self, id, make, model, year, color):
        self.make = make
        self.model = model
        self.color = color
        self.year = year
        self.capacity = 4

        if(id == None): self.id = self.to_db() # Primary Key
        else: self.id = id
    
    def __str__(self):
        return ("id: " + str(self.id) +
              "\nmake: " + self.make +
              "\nmodel: " + self.model +
              "\ncolor: " + self.color +
              "\nyear: " + str(self.year) +
              "\ncapacity: " + str(self.capacity))

    # Creates a car object from a row of the db
    @classmethod
    def from_db(cls, id):
        row = db.get_car_by_id(id)
        if(row==None): return None
        new_car = Car(row[0], row[1], row[2], row[3], row[4], row[5])
        return new_car

    # Adds a newly created car to the db and returns its id
    def to_db(self):
        return db.insert_car(self)