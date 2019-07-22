class Section:

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    def __init__(self, name, section_id, section_type, time, days, registered, closed, instructor, location, apply_penalty=True):
        self.name = name
        self.section_id = section_id
        self.section_type = section_type
        self.time = time
        self.days = days
        self.registered = registered
        self.closed = closed
        self.instructor = instructor
        self.location = location
        self.days_list = []
        self.start_end = tuple()
        self.apply_penalty = apply_penalty

        split = self.time.find("-")
        if split >= 0:
            start = time2minutes(self.time[:split])
            end = time2minutes(self.time[split + 1:-2])
            if self.time[-2:] == "pm" and end < 720:  # 12:30 pm
                start += 720
                end += 720
            if start > end:
                start -= 720
            self.start_end = (start, end)

            for i in range(5):
                if self.days.find(Section.weekdays[i]) >= 0:
                    self.days_list.append(i)

    def __str__(self):
        return (self.name + "; " + self.section_id + "; " + self.section_type + "; "
                + self.time + "; " + self.days + "; " + self.registered
                + (" (closed)" if self.closed else "") + "; "
                + self.instructor + "; " + self.location)

    def __lt__(self, other):
        return self.section_id < other.section_id


def time2minutes(time):
    split = time.find(":")
    return int(time[:split]) * 60 + int(time[split + 1:])


if __name__ == '__main__':
    pass
