class Car {
    id: number | null;
    make: string;
    model: string;
    color: string;
    year: number;
    capacity: number;

    constructor(
        id: number | null,
        make: string,
        model: string,
        color: string,
        year: number,
        capacity: number
    ) {
        this.id = id;
        this.make = make;
        this.model = model;
        this.color = color;
        this.year = year;
        this.capacity = capacity;
    }
}