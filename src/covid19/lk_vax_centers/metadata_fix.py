def get_correct_district(district, police):
    if police in ['Kalutara South']:
        district = 'Kalutara'

    if police in ['Elpitiya']:
        district = 'Galle'
    if police in ['Weligama']:
        district = 'Matara'

    if police in ['Kotmale']:
        district = 'Nuwara Eliya'

    if police in ['Kotmale']:
        district = 'Nuwara Eliya'
    if police in ['Mullaitivu']:
        district = 'Mullaitivu'
    if police in ['Kilinochchi']:
        district = 'Kilinochchi'
    if police in ['Adampan']:
        district = 'Mannar'

    if police in ['Valachchenai', 'Kokkadichcholai', 'Kaluwanchikudy']:
        district = 'Batticaloa'

    if police in ['Kuliyapitiya', 'Nikaweratiya', 'Kurunegala']:
        district = 'Kurunegala'
    if police in ['Chilaw']:
        district = 'Puttalam'

    if police in ['Bibila']:
        district = 'Moneragala'

    return district    
