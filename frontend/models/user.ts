
type DaySchedule = [number, number] | null;

type WeeklySchedule = [
    DaySchedule,
    DaySchedule,
    DaySchedule,
    DaySchedule,
    DaySchedule
];

class User {
    id: number | null;
    firstName: string;
    lastName: string;
    phone: string;
    email: string;
    gender: string;
    description: string;
    gradYear: number;
    major: string;
    schedule: WeeklySchedule | null;
    address: string | null;
    preferredPayment: string | null;
    carId: number | null;

    constructor(
        id: number | null,
        firstName: string,
        lastName: string,
        phone: string,
        email: string,
        gender: string,
        description: string,
        gradYear: number,
        major: string,
        schedule: WeeklySchedule
    ) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.phone = phone;
        this.email = email;
        this.gender = gender;
        this.description = description;
        this.gradYear = gradYear;
        this.major = major;
        this.schedule = schedule ?? [null, null, null, null, null];
        this.address = null;
        this.preferredPayment = null;
        this.carId = null;
    }
}
