from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import ScrollableContainer
from textual_plotext import PlotextPlot
from datetime import timedelta
from textual.reactive import reactive

class StatPlot(Static):
    time_fix_time=timedelta(minutes=19, seconds=35)
    left_variable=reactive("V")
    right_variable=reactive("I")
    points=reactive([])
    def on_mount(self):
        self.query_one(PlotextPlot).plt.date_form("H:M:S")
    def compose(self) -> ComposeResult:
        with ScrollableContainer():
            yield PlotextPlot()
    
    def add_point(self, point: dict, clean=False):
        self.points.append(point)
        if len(self.points)>1000:
            self.points.pop(0)
        self.watch_points(self.points)
        
    def watch_left_variable(self, value):
        self.left_variable=value
        self.watch_points(self.points)

    
    def watch_right_variable(self, value):
        self.right_variable=value
        self.watch_points(self.points)
    
    def watch_points(self, points):
        plots=(
            [p.get(self.left_variable) for  p in points],
            [p.get(self.right_variable) for  p in points],
            [
                self.query_one(PlotextPlot).plt.datetime_to_string(p.get("dateTime")-StatPlot.time_fix_time) 
                     for  p in points
            ],
        )
        unit=self.query_one(PlotextPlot)
        plt=unit.plt
        plt.clear_data()
        #normalize right plot according to left plot
        # left_array=[]
        # right_array=[]
        # if len(plots[0])>0 and len(plots[1])>0:
        
        #     max_left=max(plots[0])
        #     max_right=max(plots[1])+0.1
        #     min_left=min(plots[0])
        #     min_right=min(plots[1])
        #     for i in range(len(plots[1])):
        #         plots[1][i]=((plots[1][i]-min_right)/(max_right-min_right))*(max_left-min_left)+min_left
        #     split_arr=[0,0.3,0.6,1.1]
        #     left_array=[min_left+(max_left-min_left)*i for i in split_arr]
        #     right_array=[min_right+(max_right-min_right)*i for i in split_arr]
        #     # plt.yticks=[(old_ysticks[i]-min_right)/(max_right-min_right)*(max_left-min_left)+min_left for i in range(len(old_ysticks))]
        #     plt.text(f"M{max_right}", -1, 0)
        
        plt.plot(plots[2], plots[0], color="blue", marker=".")
        # plt.plot(plots[1], color="red", marker=".")
        # plt.yticks(left_array, [f"{i:.2f}/{j:.2f}" for i, j in zip(left_array, right_array)])
        plt.ylabel(f"{self.left_variable}")
        plt.xlabel("Time")

        unit.refresh()
    
    