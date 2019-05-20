from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, QRect, QSize

import random
import json
import os

class MainWidget(QTabWidget):
    def __init__(self, parent = None):
        super(MainWidget, self).__init__(parent)
        self.setWindowTitle("Money management!")
        self.isRunning = False

    def activate(self, userFolder):
        self.isRunning = True
        self.userFolder = userFolder
        self.initData()

        # set the size of the app
        screen = QDesktopWidget()
        screenSize = QDesktopWidget.availableGeometry(screen, self)
        self.setFixedSize(screenSize.width() * 0.8, screenSize.height())
        # set the app center
        x = (screen.rect().center() - self.rect().center()).x()
        y = 0
        self.move(x, y)

        # init tabs
        self.moneyTab = QWidget(self)
        self.distributionTab = QWidget(self)
        self.addTab(self.moneyTab, "Input")
        self.addTab(self.distributionTab, "Distribution")

        # set up Tabs
        self.getMoneyTabUI()
        self.getDistributionTabUI()

        self.show()

    @staticmethod
    def displayWarningMsgBox(displayString, parent=None):
        msgBox = QMessageBox(icon=QMessageBox.Warning, text=displayString, parent=parent)
        msgBox.setWindowTitle("Warning message")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setWindowModality(Qt.NonModal)
        msgBox.show()

    def save(self):
        try:
            data_file = open(self.file_load, 'w')
            json.dump(self.data, data_file, indent=4)
            data_file.close()
        except:
            print("Cannot save up")
            
    def initData(self):
        # base currency
        self.baseCurrency = 'VND'

        # file_name
        currentYear = str(QDate.currentDate().year())
        # for example : ty/2019.json
        self.file_load = self.userFolder + r'/' + currentYear + '.json' 

        # init data
        # assign
        self.spend_data = [[] for month in range(13)]
        self.earn_data = [[] for month in range(13)]
        for month in range(1, 13):
            # get the nunmber of days in particular month
            numbDaysInMonth = QDate(2019, month, 1).daysInMonth()
            # 0 for each day
            # + 1 because there's no [0] day
            self.spend_data[month] = [0] * (numbDaysInMonth + 1)
            self.earn_data[month] = [0] * (numbDaysInMonth + 1)

        # try creating a new folder, and its ok if it exista
        os.makedirs(self.userFolder, exist_ok=True)

        try:
            data_file = open(self.file_load, 'r')
        except:
            # create file
            tmp_file = open(self.file_load, 'w+')
            tmp_data = {}
            json.dump(tmp_data, tmp_file)
            tmp_file.close()
            data_file = open(self.file_load, 'r')

        self.data = json.load(data_file)

        for month in range(1, 13):
            # if haven't had that month yet
            if str(month) not in self.data.keys():
                self.data[str(month)] = {str(day): [] for day in range(QDate(2019, month, 1).daysInMonth() + 1)}

        print(self.data)

        for month in range(1, 13):
            numbDaysInMonth = QDate(2019, month, 1).daysInMonth()
            for day in range(numbDaysInMonth + 1):
                # turn the key into string
                month_str = str(month)
                day_str = str(day)
                for thing in self.data.get(month_str).get(day_str):
                    if thing['amount'] > 0:
                        self.updateSpendData(QDate(2019, month, day), thing)
                    else:
                        self.updateEarnData(QDate(2019, month, day), thing)

        data_file.close()

    # return the ratio between the passed-in currency and the baseCurrency
    def currencyRatio(self, currency):
        value = {'VND': 1,
        'YEN': 212,
        'USD': 23300}
        if currency not in value.keys():
            self.displayWarningMsgBox('We don\'t have this currency converter', parent=self)
            return 1
        else:
            return value[currency] / value[self.baseCurrency]

    def updateSpendData(self, date, thing):
        month = date.month()
        day = date.day()
        try:
            self.spend_data[month][day] += thing['amount'] * self.currencyRatio(thing['currency'])
        except:
            print("Error in month {} day {}".format(month, day))

    def updateEarnData(self , date, thing):
        month = date.month()

        # the increase in earn_data will be splitted to each day
        inc_amount = thing['amount'] * self.currencyRatio(thing['currency']) / len(self.earn_data)
        if inc_amount < 0:
            inc_amount = abs(inc_amount)

        for day in range(len(self.earn_data[month])):
            self.earn_data[month][day] += inc_amount 

    def uploadData(self, date, thing):
        month = date.month()
        day = date.day()
        amount = thing['amount']
        # add to Data
        self.data[str(month)][str(day)].append(thing)

        print("Date: ")
        print(date)
        # spend data
        if amount > 0:
            self.updateSpendData(date, thing)
        else:
            self.updateEarnData(date, thing)
    
    def getMoneyTabUI(self):
        # graph format
        spend_data_fmt = 'r.-'
        earn_data_fmt = 'y-'
        
        # init graph
        # graph
        figure = Figure()
        canvas = FigureCanvas(figure)

        axes = figure.add_subplot(111)

        axes.clear()
        axes.plot(self.spend_data[QDate.currentDate().month()], spend_data_fmt)
        axes.plot(self.earn_data[QDate.currentDate().month()], earn_data_fmt)
        canvas.draw()

        def monthChanged(year, month):
            # clear previous graph
            axes.clear()
            axes.plot(self.spend_data[month], spend_data_fmt)
            axes.plot(self.earn_data[month], earn_data_fmt)
            canvas.draw()

        # calendar
        calendar = QCalendarWidget()
        calendar.currentPageChanged.connect(monthChanged)


        thing_line = QLineEdit()
        thing_line.setPlaceholderText("Thing")
        thing_label = QLabel('Thing: ')
        thing_label.setBuddy(thing_line)

        # thing lines
        thing_layout = QHBoxLayout()
        thing_layout.addWidget(thing_label)
        thing_layout.addWidget(thing_line)

        def spend():
            if len(thing_line.text()) == 0:
                self.displayWarningMsgBox("Fill what you spent!", parent=self)
                return 

            if len(cost_line.text()) == 0:
                self.displayWarningMsgBox("Fill how much you spent!", parent=self)
                return

            if not cost_line.text().isdigit():
                self.displayWarningMsgBox("The amount contains non-number character", parent=self)
                return

            selected_date = calendar.selectedDate()
            spend_month = selected_date.month()
            spend_day = selected_date.day()
            
            # set up thing
            thing = {}
            thing['name'] = thing_line.text()
            thing['currency'] = unit_combo_box.currentText()
            thing['amount'] = int(cost_line.text(), 10)
            if thing['currency'] == 'VND':
                thing['amount'] *= 1000
            
            self.uploadData(selected_date, thing)

            # reset the text to EMPTY
            thing_line.setText("")
            cost_line.setText("")

            axes.clear()
            axes.plot(self.spend_data[spend_month], spend_data_fmt)
            axes.plot(self.earn_data[spend_month], earn_data_fmt)
            canvas.draw()

        # spend button
        spend_btn = QPushButton('Spend')
        spend_btn.clicked.connect(spend)

        cost_line = QLineEdit()
        cost_line.setPlaceholderText("Cost")
        cost_label = QLabel('Cost :')
        cost_label.setBuddy(cost_line)
        thousand_label = QLabel('000')
        thousand_label.setBuddy(cost_line)
        unit_combo_box = QComboBox()
        unit_combo_box.addItems(["VND", "YEN", "USD"])
        unit_combo_box.currentTextChanged.connect(lambda cur: currencyChange(thousand_label, cur))

        def currencyChange(label, currency):
            label.hide()
            if currency == 'VND':
                label.show()

        # cost lines
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(cost_label)
        cost_layout.addWidget(cost_line)
        cost_layout.addWidget(thousand_label)
        # hide until vietnamese
        if unit_combo_box.currentText() != 'VND':
            thousand_label.hide()
        cost_layout.addWidget(unit_combo_box)

        # source line
        source_line = QLineEdit()
        source_line.setPlaceholderText("Source")
        source_label = QLabel('Source')
        source_label.setBuddy(source_line)

        source_layout = QHBoxLayout()
        source_layout.addWidget(source_label)
        source_layout.addWidget(source_line)

        # amount line
        amount_line = QLineEdit()
        amount_line.setPlaceholderText("Amount")
        amount_label = QLabel('Amount')
        amount_label.setBuddy(amount_line)
        thousand_label2 = QLabel('000')
        thousand_label2.setBuddy(amount_line)
        unit_combo_box2 = QComboBox()
        unit_combo_box2.addItems(["VND", "YEN", "USD"])
        unit_combo_box2.currentTextChanged.connect(lambda cur: currencyChange(thousand_label2, cur))

        amount_layout = QHBoxLayout()
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(amount_line)
        amount_layout.addWidget(thousand_label2)
        if unit_combo_box2.currentText() != 'VND':
            thousand_label2.hide()
        amount_layout.addWidget(unit_combo_box2)

        def earn():
            if len(source_line.text()) == 0:
                self.displayWarningMsgBox("Fill where you get money!", parent=self)
                return 

            if len(amount_line.text()) == 0:
                self.displayWarningMsgBox("Fill how much you earn!", parent=self)
                return

            if not amount_line.text().isdigit():
                self.displayWarningMsgBox("The amount contains non-number character", parent=self)
                return

            selected_date = calendar.selectedDate()
            earn_month = selected_date.month()
            
            # set up thing
            thing = {}
            thing['name'] = source_line.text()
            thing['currency'] = unit_combo_box2.currentText()
            # earn is negative (???)
            thing['amount'] = - int(amount_line.text(), 10)
            if thing['currency'] == 'VND':
                thing['amount'] *= 1000
            
            self.uploadData(selected_date, thing)

            # reset text
            source_line.setText("")
            amount_line.setText("")

            axes.clear()
            try:
                axes.plot(self.earn_data[earn_month], earn_data_fmt)
                axes.plot(self.spend_data[earn_month], spend_data_fmt)
            except:
                print("Earn data: ")
                print(self.earn_data[QDate.currentDate().month()])
                print("Spend data:")
                print(self.spend_data[QDate.currentDate().month()])
            canvas.draw()

        # earn button
        earn_btn = QPushButton('Earn')
        earn_btn.clicked.connect(earn)

        # 2 tabs for spend and ear
        spend_tab = QWidget()
        spend_tab_layout = QVBoxLayout()
        spend_tab_layout.addLayout(thing_layout)
        spend_tab_layout.addLayout(cost_layout)
        spend_tab_layout.addWidget(spend_btn)
        spend_tab.setLayout(spend_tab_layout)

        earn_tab = QWidget()
        earn_tab_layout = QVBoxLayout()
        earn_tab_layout.addLayout(source_layout)
        earn_tab_layout.addLayout(amount_layout)
        earn_tab_layout.addWidget(earn_btn)
        earn_tab.setLayout(earn_tab_layout)

        spend_earn_tab = QTabWidget()
        spend_earn_tab.addTab(spend_tab, "Spend")
        spend_earn_tab.addTab(earn_tab, "Earn")

        # upper layout
        upper_layout = QHBoxLayout()
        upper_layout.addWidget(spend_earn_tab)
        upper_layout.addWidget(calendar)

        # outmost layout
        outmost_layout = QVBoxLayout()
        outmost_layout.addLayout(upper_layout)
        outmost_layout.addWidget(canvas)

        self.moneyTab.setLayout(outmost_layout)

    def getDistributionTabUI(self):
        month_combo_box = QComboBox(parent=self.distributionTab)
        month_combo_box.addItem('')
        month_combo_box.addItems([str(i) for i in range(1, 13)])
        month_label = QLabel('Month: ', parent=self.distributionTab)
        month_label.setBuddy(month_combo_box)

        year_combo_box = QComboBox(parent=self.distributionTab)
        year_combo_box.addItem('')
        year_combo_box.addItems(['2019'])
        year_label = QLabel('Year :', parent=self.distributionTab)
        year_label.setBuddy(year_combo_box)

        plot_btn = QPushButton('Plot the month', parent=self.distributionTab)

        # draw a pie chart
        pie_figure = Figure()
        pie_canvas = FigureCanvas(pie_figure)
        pie_canvas.setParent(self.distributionTab)

        # the [0] will be left out
        pie_labels = [[] for month in range(13)]
        pie_sizes = [[] for month in range(13)]

        def plot_pie():
            # for 'Other' size
            size = 0
            current_month = month_combo_box.currentText()
            if current_month == '':
                self.displayWarningMsgBox('Choose the month to draw!', parent=self)
                return
            current_month = int(current_month)
            current_year = year_combo_box.currentText()
            if current_year == '':
                self.displayWarningMsgBox('Choose the year to draw!', parent=self)
                return
            current_year = int(current_year)
            
            money_spent = 0

            # reset 
            pie_labels[current_month] = []
            pie_sizes[current_month] = []
            shopping = {}

            # get the money spent
            # +1 again because the [0] is not counted
            for day in range(QDate(current_year, int(current_month), 1).daysInMonth() + 1):
                for thing in self.data.get(str(current_month)).get(str(day)):
                    print(thing)
                    name = thing['name']
                    amount = (thing['amount'] * self.currencyRatio(thing['currency']) )
                    if amount > 0:
                        money_spent += amount
                        if name in shopping.keys():
                          shopping[name] += amount
                        else:
                            shopping[name] = amount

            for name in shopping.keys():
                # if it dominates at least 5% of the money spent
                if (shopping[name] / money_spent) >= 0.05:
                    pie_labels[current_month].append(name)
                    pie_sizes[current_month].append(shopping[name] / money_spent)
                    size += shopping[name] / money_spent
            # anything < 5%
            if 1 - size > 0.005:
                pie_labels[current_month].append('Others')
                pie_sizes[current_month].append(1 - size)
                    
            pie_axes = pie_figure.add_subplot(111)
            pie_axes.clear()
            pie_axes.pie(pie_sizes[current_month], labels=pie_labels[current_month], startangle=90, autopct="%1.2f%%", radius=1.2, shadow=True)
            # pie_axes.axis("Equal")

            pie_canvas.draw()

        # Decorate
        dis_pos = self.distributionTab.mapTo(self, self.pos())
        month_pos = month_label.mapTo(self, self.pos())

        # move month label to top left corner
        month_label.setFixedSize(self.width() / 10, self.height() / 20)
        month_label.move(50, 20)

        # put combo box next to month_label
        month_combo_box.setFixedSize(month_label.width(), month_label.height())
        month_combo_box.move(month_label.x() + month_label.width() , month_label.y())

        year_label.setFixedSize(self.width() / 10, self.height() / 20)
        year_label.move(month_label.x(), month_label.y() + month_label.height() + 10)

        # put combo box next to year_label
        year_combo_box.setFixedSize(year_label.width(), year_label.height())
        year_combo_box.move(year_label.x() + year_label.width(), year_label.y())

        plot_btn.setFixedSize(150, 50)
        # put in the middle
        plot_btn.move(year_label.x() + (year_label.width() + year_combo_box.width()) / 2 - plot_btn.width() / 2
                            , year_label.y() + year_label.height() + 10 )
        plot_btn.clicked.connect(plot_pie)

        # put pie_chart below
        pie_canvas.setFixedSize(800, 600)
        pie_canvas.move(month_combo_box.x() + month_combo_box.width() + 10, month_combo_box.y() )
        
    
