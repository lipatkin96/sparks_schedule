from Schedule import Schedule
from ScheduleExtractionExcelType import ScheduleExtractionExcelType, EmployeeCard


class EmployeeFavor:
    def __init__(self):
        self.ghostNames = {
            'Даша': 1,
            'Маша': 2,
            'Саша': 3,
            'Лада': 4,
            'Артур': 5
        }
        self.eldersNames = {
            1: 'Вован',
            2: 'Люба'
        }

        # дни, в которых есть нецелые смены
        self.partTimeDays = {
            4: 0.5,
            5: 0.5
        }
        self.ghostLimits = {
            1: 3.5,
            2: 3.5,
            3: 3,
            4: 3,
            5: 1
        }
        self.undesirableGhostDays = {
            1: [1, 2],
            2: [3, 5, 6],
            3: [],
            4: [1, 2, 3, 7],
            5: []
        }

        self._week = range(1, 7 + 1)
        self._oneTimeWeek = range(1, 3 + 1)
        self._pairWeek = range(3 + 1, 7 + 1)
        self._shiftDayLen = [self.partTimeDays.get(i)
                           if i in self.partTimeDays else 1.0 for i in self._week]

    def toExcel(self, schedule: Schedule) -> ScheduleExtractionExcelType:
        excelDict = ScheduleExtractionExcelType()

        for ghostName, ghostId in self.ghostNames.items():
            turnList = []
            employeeCard = EmployeeCard(ghostName, False)

            for i, day in zip(schedule.ghostOneTime, self._oneTimeWeek):
                if i == ghostId:
                    turnList.append((day, 1.0, 'Hall'))

            for p, day in zip(schedule.ghostPair, self._pairWeek):
                if ghostId == p[0] or ghostId == p[1]:
                    turnList.append((day, self._shiftDayLen[day - 1] if ghostId == p[0] else 1.0, 'Hall'))

            excelDict[employeeCard] = turnList

        return excelDict

    def pairDayStart(self):
        return self._pairWeek[0]

    def fromExcel(self, excelSchedule: ScheduleExtractionExcelType) -> Schedule:
        schedule = Schedule(self.pairDayStart())

        for ghostCard, ghostSchedule in excelSchedule.items():
            # skip eldermen
            if ghostCard.IsElder is True:
                continue
            ghostId = self.ghostNames[ghostCard.Name]
            for day, shiftLen, _ in ghostSchedule:
                if day < self.pairDayStart():
                    schedule.ghostOneTime[day - 1] = ghostId
                elif day <= 7:
                    pair = schedule.ghostPair[day - self.pairDayStart()]
                    if shiftLen < 1.0 - 1e5 or pair[0] == 0:
                        pair = (ghostId, pair[1])
                    elif pair[1] == 0:
                        pair = (pair[0], ghostId)
                    else:
                        print("Error: schedule is not parsed correctly. "
                              "Repeated schedule in one day is found.")

                    schedule.ghostPair[day - self.pairDayStart()] = pair

        if not schedule.isValid():
            print("Error: schedule is not parsed correctly.")

        return schedule

    def print(self, schedule: Schedule):
        week = range(1, 7 + 1)
        nameMaxLen = 6
        print(''.rjust(nameMaxLen + 1), end='')
        for day in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']:
            print(day.rjust(4), end='')
        print()

        # todo: don't forget it
        # print(self.eldersNames[1].rjust(nameMaxLen) + ':', end='')
        # for i in week:
        #     turnName = 'C'
        #     print((turnName if i in self.schedule.vovan else 'x').rjust(4), end='')
        # print()
        # print(self.eldersNames[2].rjust(nameMaxLen) + ':', end='')
        # for i in week:
        #     turnName = 'C'
        #     print((turnName if i not in self.schedule.vovan else 'x').rjust(4), end='')
        # print()
        #
        # print('---------------------'.rjust((nameMaxLen + 1 + 7 * 4) // 5 * 4))

        oneTimeWeek = [1, 2, 3]
        for [name, ghostId] in self.ghostNames.items():
            print(name.rjust(nameMaxLen) + ':', end='')
            for day in week:
                if day in oneTimeWeek:
                    turnName = 'C'
                    if day in self.undesirableGhostDays[ghostId]:
                        turnName = 'S'
                    print((turnName if schedule.ghostOneTime[day - 1] == ghostId else 'x')
                          .rjust(4), end='')
                else:
                    turnName = 'C2' if (day in self.partTimeDays
                                        and ghostId == schedule.ghostPair[day - 4][0]) else 'С'
                    if day in self.undesirableGhostDays[ghostId]:
                        turnName = turnName.replace('C', 'S')
                    print((turnName if ghostId in schedule.ghostPair[day - 4] else 'x')
                          .rjust(4), end='')
            print()