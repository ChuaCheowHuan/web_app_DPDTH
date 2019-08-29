CREATE TABLE passengers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    flight_id INTEGER REFERENCES flights
);

INSERT INTO passengers (name, flight_id) VALUES ('Alice', 1);
INSERT INTO passengers (name, flight_id) VALUES ('Bob', 1);
INSERT INTO passengers (name, flight_id) VALUES ('Charlie', 2);
INSERT INTO passengers (name, flight_id) VALUES ('Dave', 2);
INSERT INTO passengers (name, flight_id) VALUES ('Erin', 4);
INSERT INTO passengers (name, flight_id) VALUES ('Frank', 6);
INSERT INTO passengers (name, flight_id) VALUES ('Grace', 6);


SELECT origin, destination, name FROM flights INNER JOIN passengers ON passengers.flight_id = flights.id;
SELECT origin, destination, name FROM flights JOIN passengers ON passengers.flight_id = flights.id;
SELECT origin, destination, name FROM flights LEFT OUTER JOIN passengers ON passengers.flight_id = flights.id;
SELECT origin, destination, name FROM flights RIGHT OUTER JOIN passengers ON passengers.flight_id = flights.id;
