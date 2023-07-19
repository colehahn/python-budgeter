import datetime
import math
import matplotlib.pyplot as plt
from typing import Optional
from abc import ABC


class Payment(ABC):
    description: str
    amount: float
    color: Optional[str]

    def occursOnDay(self, date: datetime.date):
        return NotImplemented


class RecurringPayment(Payment):
    def __init__(
        self,
        description: str,
        amount: float,
        frequency: int,
        start: tuple[int, int, int],
        end: Optional[tuple[int, int, int]] = None,
        color: Optional[str] = None,
    ):
        self.description = description
        self.amount = amount
        self.frequency = frequency
        self.start = datetime.date(*start)
        self.color = color
        if end != None:
            self.end = datetime.date(*end)  # type: ignore
        else:
            self.end = None  # type: ignore

    def occursOnDay(self, date: datetime.date):
        if self.end == None:
            return date > self.start and (date - self.start).days % self.frequency == 0
        else:
            return (
                date > self.start
                and date < self.end
                and (date - self.start).days % self.frequency == 0
            )


class OneTimePayment(Payment):
    def __init__(
        self,
        description: str,
        amount: float,
        date: tuple[int, int, int],
        color: Optional[str] = None,
    ):
        self.description = description
        self.amount = amount
        self.date = datetime.date(*date)
        self.color = color

    def occursOnDay(self, date: datetime.date):
        return self.date == date


###########################################################################
##################### CONFIGURATION: ######################################
payments = []

startingmoney = 0  # bank accounts minus credit card balances
startingdate = datetime.date(2023, 7, 17)
NUM_MONTHS = 6
###########################################################################
###########################################################################


def pad_with_zero(n):
    if len(n) < 2:
        return "0" + n
    else:
        return n


def rgb_to_hex(r, g, b):
    return (
        "#"
        + pad_with_zero(hex(r)[2:])
        + pad_with_zero(hex(g)[2:])
        + pad_with_zero(hex(b)[2:])
    )


def get_color(payment: Payment):
    if payment.color:
        return payment.color
    else:
        val = max(0, int(200 - math.log(abs(payment.amount), 2) ** 2))
        return (
            rgb_to_hex(255, val, val)
            if payment.amount < 0
            else rgb_to_hex(val, 255, val)
        )


dailymonies = []
days = []
points = []
currentmoney = startingmoney
currentdate = startingdate
for i in range(30 * NUM_MONTHS):
    for payment in payments:
        if payment.occursOnDay(currentdate):
            points.append(
                (
                    currentdate - datetime.timedelta(days=1),
                    currentmoney,
                    payment.description,
                    get_color(payment),
                    payment.amount,
                )
            )
            currentmoney += payment.amount
    dailymonies.append(currentmoney)
    days.append(currentdate)
    currentdate += datetime.timedelta(days=1)

labels = [point[2] for point in points]
colors = [point[3] for point in points]
amounts = [point[4] for point in points]

fig, ax = plt.subplots()
plt.title("budget")
plt.plot(days, dailymonies)
sc = plt.scatter(
    [point[0] for point in points],
    [point[1] for point in points],
    c=colors,
)
annot = ax.annotate(
    "",
    xy=(0, 0),
    xytext=(20, 20),
    textcoords="offset points",
    bbox=dict(boxstyle="round", fc="w"),
    arrowprops=dict(arrowstyle="->"),
)
annot.set_visible(False)


def update_annot(ind):
    # TODO: think about what I want to happen if we are hovering over two overlapping points
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = "{}, {}".format(
        " ".join([str(amounts[n]) for n in ind["ind"]]),
        " ".join([labels[n] for n in ind["ind"]]),
    )
    annot.set_text(text)
    annot.get_bbox_patch().set_facecolor(colors[ind["ind"][0]])
    annot.get_bbox_patch().set_alpha(0.4)


def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()


plt.xlabel("date")
plt.ylabel("money")
fig.canvas.mpl_connect("motion_notify_event", hover)
plt.show()
