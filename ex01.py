import pandas as pd
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QRadioButton, QButtonGroup
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import sys
plt.rcParams['font.sans-serif'] = ['SimHei']
class HeightAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.df = self.load_data()
        self.init_ui()

    def load_data(self):
        """加载CSV数据并处理格式"""
        try:
            df = pd.read_csv('height.csv')
            # 清理列名
            df.columns = df.columns.str.strip()
            # 确认关键列是否存在
            required_columns = {'Country', 'Sex', 'Year', 'Age group', 'Mean height'}
            if not required_columns.issubset(df.columns):
                raise ValueError("CSV文件缺少必要列！")
            return df
        except Exception as e:
            print(f"数据加载错误: {e}")
            return pd.DataFrame(columns=required_columns)

    def init_ui(self):
        self.setWindowTitle("中国男孩女孩身高变化信息分析")
        self.setGeometry(100, 100, 900, 700)

        # 主布局
        main_layout = QVBoxLayout()

        # 1. 顶部标题
        title = QLabel("中国男孩女孩身高变化信息分析")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(title)

        # 2. 控制面板
        control_panel = QHBoxLayout()

        # 性别选择
        gender_group = QButtonGroup(self)
        self.gender_all = QRadioButton("全部")
        self.gender_boys = QRadioButton("男性")
        self.gender_girls = QRadioButton("女性")
        gender_style = "QRadioButton { font-size: 14px; margin-right: 15px; }"
        for btn in [self.gender_all, self.gender_boys, self.gender_girls]:
            btn.setStyleSheet(gender_style)
        gender_group.addButton(self.gender_all)
        gender_group.addButton(self.gender_boys)
        gender_group.addButton(self.gender_girls)
        self.gender_all.setChecked(True)

        control_panel.addWidget(QLabel("性别:"))
        control_panel.addWidget(self.gender_all)
        control_panel.addWidget(self.gender_boys)
        control_panel.addWidget(self.gender_girls)

        # 年份选择
        years = sorted(self.df['Year'].unique()) if not self.df.empty else range(1985, 2020)
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(y) for y in years])
        self.year_combo.setStyleSheet("QComboBox { min-width: 100px; }")
        control_panel.addSpacing(20)
        control_panel.addWidget(QLabel("年份:"))
        control_panel.addWidget(self.year_combo)
        control_panel.addStretch()
        main_layout.addLayout(control_panel)

        # 3. 图表区域
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas, stretch=1)

        # 4. 底部信息
        footer = QLabel(
            "1985~2019年 中国男孩女孩5~19岁年龄段的平均身高变化情况\n"
            "数据来源: height.csv | 南昌大学 计算机科学与技术系 潘咏晴 9109223190"
        )
        footer.setStyleSheet("font-size: 12px; color: #666; margin-top: 15px;")
        main_layout.addWidget(footer)

        # 信号连接
        for btn in gender_group.buttons():
            btn.toggled.connect(self.update_plot)
        self.year_combo.currentTextChanged.connect(self.update_plot)
        self.setLayout(main_layout)
        self.update_plot()

    def update_plot(self):
        """更新图表数据"""
        try:
            year = int(self.year_combo.currentText())
            self.ax.clear()
            # 筛选中国数据
            df_china = self.df[(self.df['Country'] == 'China') & (self.df['Year'] == year)]
            if df_china.empty:
                self.ax.text(0.5, 0.5, "无可用数据", ha='center', va='center')
                self.canvas.draw()
                return

            # 按年龄组排序
            age_groups = sorted(df_china['Age group'].unique())
            x = range(len(age_groups))
            width = 0.35

            # 绘制男性数据
            if self.gender_all.isChecked() or self.gender_boys.isChecked():
                boys_data = df_china[df_china['Sex'] == 'Boys'].sort_values('Age group')
                boys_bars = self.ax.bar(
                    [i - width / 2 for i in x],
                    boys_data['Mean height'],
                    width,
                    label='男性',
                    color='#1f77b4',
                    yerr=boys_data['standard error'] if 'standard error' in df_china.columns else None,
                    capsize=3
                )

                # 在男性柱子上方添加数值标签
                for bar in boys_bars:
                    height = int(bar.get_height())
                    self.ax.text(bar.get_x() + bar.get_width() / 2.,
                                 height + 1,  # 在柱顶上方1单位处显示
                                 f'{height}',  # 显示1位小数
                                 ha='center', va='bottom',
                                 fontsize=8)

            # 绘制女性数据
            if self.gender_all.isChecked() or self.gender_girls.isChecked():
                girls_data = df_china[df_china['Sex'] == 'Girls'].sort_values('Age group')
                girls_bars = self.ax.bar(
                    [i + width / 2 for i in x],
                    girls_data['Mean height'],
                    width,
                    label='女性',
                    color='#ff7f0e',
                    yerr=girls_data['standard error'] if 'standard error' in df_china.columns else None,
                    capsize=3
                )

                # 在女性柱子上方添加数值标签
                for bar in girls_bars:
                    height = int(bar.get_height())
                    self.ax.text(bar.get_x() + bar.get_width() / 2.,
                                 height + 1,
                                 f'{height}',
                                 ha='center', va='bottom',
                                 fontsize=8)

            # 图表装饰
            self.ax.set_xticks(x)
            self.ax.set_xticklabels([f"{age}岁" for age in age_groups])
            self.ax.set_xlabel("年龄组", fontsize=12)
            self.ax.set_ylabel("平均身高 (cm)", fontsize=12)
            self.ax.set_title(f"{year}年中国儿童青少年身高对比", fontsize=14, pad=20)
            self.ax.legend(loc='upper left')
            self.ax.grid(axis='y', linestyle='--', alpha=0.7)

            # 自动调整Y轴范围
            min_height = df_china['Mean height'].min() * 0.95
            max_height = df_china['Mean height'].max() * 1.05
            self.ax.set_ylim(min_height, max_height)
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"绘图错误: {e}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeightAnalysisApp()
    window.show()
    sys.exit(app.exec())