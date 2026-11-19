class User {
    firstName: string;
    lastName: string;
    phone: string;
    email: string;
    gender: string;
    description: string;
    gradYear: number;
    major: string;
    schedule: [number, number];
    address: string;
    preferredPayment: string;
    carId: string;

    constructor(firstName: string, lastName: string, phone: string, email: string, gender: string, description: string, gradYear: number, major: string, schedule: [number, number], address: string, preferredPayment: string, carId: string) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.phone = phone;
        this.email = email;
        this.gender = gender;
        this.description = description;
        this.gradYear = gradYear;
        this.major = major;
        this.schedule = schedule;
        this.address = address;
        this.preferredPayment = preferredPayment;
        this.carId = carId;
    }
}