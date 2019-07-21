class Section:

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    starting_minutes = [0, 1440, 2880, 4320, 5760]

    def __init__(self, name, section_id, section_type, time, days, registered, closed, instructor, location):
        self.name = name
        self.section_id = section_id
        self.section_type = section_type
        self.time = time
        self.days = days
        self.registered = registered
        self.closed = closed
        self.instructor = instructor
        self.location = location
        self.time_durations = []

        split = self.time.find("-")
        if split >= 0:
            start = time2minutes(self.time[:split])
            end = time2minutes(self.time[split + 1:-2])
            if self.time[-2:] == "pm":
                start += 720
                end += 720

            for i in range(5):
                if self.days.find(Section.weekdays[i]) >= 0:
                    self.time_durations.append(
                        (start + Section.starting_minutes[i], end + Section.starting_minutes[i]))

    def __str__(self):
        return (self.name + "; " + self.section_id + "; " + self.section_type + "; "
                + self.time + "; " + self.days + "; " + self.registered
                + (" (closed)" if self.closed else "") + "; "
                + self.instructor + "; " + self.location)


def time2minutes(time):
    split = time.find(":")
    return int(time[:split]) * 60 + int(time[split + 1:])


if __name__ == '__main__':
    pass
