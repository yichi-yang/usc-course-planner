from section import Section
import pickle
import bisect
import matplotlib.pyplot as plt


def show_time_table(sections):
    fig, ax = plt.subplots(figsize=(16, 9))

    for section in sections:
        for day in section.days_list:
            bar_bottom = section.start_end[0]
            bar_height = section.start_end[1] - section.start_end[0]
            ax.bar(day, bar_height, width=0.92,
                   bottom=bar_bottom, linewidth=0, fc='#3CA730')
            description = (section.name
                           + " (" + section.section_id + ") "
                           + section.section_type)
            ax.text(day, bar_bottom + bar_height / 2, description,
                    horizontalalignment='center', verticalalignment='center',
                    fontfamily='Nirmala UI', color='white', fontsize='large')

    ax.set_axisbelow(True)
    ax.minorticks_on()
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xticks([0.5, 1.5, 2.5, 3.5], minor=True)
    ax.set_yticks(range(5*60, 24*60, 60))
    ax.set_yticklabels(
        [str(time) + ":00" for time in range(5, 24)], fontfamily='Nirmala UI')
    ax.set_yticks(range(5*60 + 30, 24*60, 60), minor=True)
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(23*60, 5*60)
    ax.xaxis.tick_top()
    ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri"],
                       fontfamily='Nirmala UI', fontsize='x-large')

    # ax.grid(which = 'major', visible = False)
    ax.grid(which='minor', axis='x', linewidth=0.5, alpha=0.8)
    ax.grid(which='major', axis='y', linewidth=0.5, alpha=0.8)
    ax.grid(which='minor', axis='y', linewidth=0.5, alpha=0.3)
    ax.tick_params(which='both', top=False,  left=False,
                   right=False, bottom=False)
    ax.spines['bottom'].set_color("#bababa")
    ax.spines['top'].set_color("#bababa")
    ax.spines['left'].set_color("#bababa")
    ax.spines['right'].set_color("#bababa")
    plt.show()


if __name__ == '__main__':
    with open("one_combination.pickle", "rb") as ifile:
        sections = pickle.load(ifile)
        show_time_table(sections)
