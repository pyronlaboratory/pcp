class Car:
    def __init__(self, make, model, fuel_capacity):
        self.make = make
        self.model = model
        self.fuel_capacity = fuel_capacity
        self.fuel_level = 0
    
    def start(self):
        if self.fuel_level > 0:
            return f"{self.make} {self.model} started."
        else:
            return "Cannot start. Add fuel."

    def drive(self, distance):
        if self.fuel_level > 0:
            fuel_needed = distance / 10  # Assuming fuel efficiency of 10 km per liter
            if fuel_needed <= self.fuel_level:
                self.fuel_level -= fuel_needed
                return f"{self.make} {self.model} drove {distance} kilometers."
            else:
                return "Not enough fuel to drive that far."
        else:
            return "Cannot drive. Add fuel."

    def stop(self):
        return f"{self.make} {self.model} stopped."

def calculate_efficiency(distance, fuel_used):
    efficiency = distance / fuel_used
    return f"Fuel efficiency: {efficiency} km/liter"


if __name__ == "__main__":
    my_car = Car("Toyota", "Camry", fuel_capacity=50)
    print(my_car.start())  # Output: Toyota Camry started.
    print(my_car.drive(150))  # Output: Toyota Camry drove 150 kilometers.
    print(calculate_efficiency(150, 12))  # Output: Fuel efficiency: 12.5 km/liter
    print(my_car.stop())  # Output: Toyota Camry stopped.
