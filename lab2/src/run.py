import lab2.hh as hh

vacancy = 'python-разработчик'
getter = hh.VacancyGetter(vacancy)
vacancies = getter.get_all_vacancies()

print("Прочитано {} вакансий".format(len(vacancies)))

classifier = hh.VacancyRangeClassifier(vacancies)
classes = classifier.classify()

drawer = hh.PlotDrawer(
    title='Количество предложений по зарплатам: {}'.format(vacancy),
    xlabel='Зарплата',
    ylabel='Количество предложений'
)
drawer.draw(classes)

classifier = hh.VacancyMedianClassifier(vacancies)
classes = classifier.classify()

classes = sorted(classes, key=lambda x: x['value'], reverse=True)
drawer = hh.PlotDrawer(
    title='Медианные зарплаты по городам: {}'.format(vacancy),
    xlabel='Город',
    ylabel='Медианная зарплата, руб.'
)
drawer.draw(classes[:10])


