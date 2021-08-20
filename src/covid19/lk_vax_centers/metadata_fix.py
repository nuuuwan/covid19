CORRECT_FUZZY_KEYS = set(
    [
        'BDLLGRNDRKTTMHFFCGRNDRKTT',
        'BTTCLVKRMHFFCVKR',
        'NRDHPRKKRWDSTRCTHSPTLKKRW',
        'NRDHPRNCHCHYGMHRVLVDYLY',
        'BDLLLNGLMHFFCLNGL',
        'GLLKTWLKMBRGMWMHVDYLY',
        'GMPHNGMBMNKLYSTNTHNYSCHRCH',
        'GMPHNTTMBWKNDVHRY',
        'KNDYNWLPTYHLGRKYSRSMNVDYLY',
    ]
)
INCORRECT_FUZZY_KEYS = set(
    [
        'NRDHPRNCHCHYGMMBGSWWVDYLY',
        'BDLLMHYNGNYMHFFCMHYNGNY',
        'CLMBHNWLLRMNCTHLCCLLGWLKNN',
        'GLLLPTYKTLVTGLSTTFFC',
        'KLTRMLLNYPTHGMWVHRY',
        'KLTRMTGMMBTHNNSTTPRMSS',
        'KGLLMWNLLMRTHWLCMMNTYHLL',
        'KRNGLWRMBGDRKNDRGHMDTHTHVDYLY',
        'PTTLMPTTLMVSDRRMVHRY',
        'BDLLHLDMMLLHDWRYCLLG',
        'BDLLVPRNGMHLKTWHRSBDRRMY',
        'GMPHKDWTNLMMHRVDYLY',
        'HMBNTTSRYWWNDWWVHRY',
        'KLTRWDDWGMXPRTCNTR',
        'KNDYDDMBRDDMBRSCNDRYCLLG',
        'KNDYDDMBRMHNDPRMRYSCHL',
        'KNDYKNDYPRDNYYTHSRVCSCNCL',
    ]
)

FUZZY_KEY_TO_ALT_NAME = {
    'GMPHNTTMBWDHTHKNDRJMHVHRY': 'Dhathukanda Purana Rajamaha Viharaya',
    'GMPHNTTMBWNDGDVHRY': 'Bodhimalu Viharaya - Undugoda',
    'GMPHPLYGDGGBDCMMNTYHLL': 'PCAG Community Center',
    'TRNCMLPLMDDPLMDDBSHSPTL': 'Base Hospital - Pulmoddai',
    'NRDHPRTHNTHRMLTHNTHRMLRJMHVHRY': 'Tantirimale Rajamaha Viharaya',
    'BDLLLNGLLNGLHSPTL': 'District Hospital - Lunugala',
    'BDLLMHYNGNYMHYNGNYBSHSPTL': 'Base Hospital - Mahiyanganaya',
    'BDLLVPRNGMVPRNGMHSPTL': 'Divisional Hospital - Uva Paranagama',
    'BTTCLKLWNCHKDYKLWNCHKDYHSPTL': 'Base Hospital - Kaluwanchikudy',
    'BTTCLKLWNCHKDYMHFFCKLWNCHKDY': 'Medical Officer of Health Kaluwanchikudy',
    'CLMBGDYNMHFFCGDYN': 'MOH Egodauyana',
    'CLMBPDKKGHPDKK': 'Padukka Divisional Hospital',
    'HMBNTTTSSMHRMDBRWWPRSDNTSPRMRYSCHL': 'Debarawewa President\'s College',
    'KGLLMWNLLRNDWLMHVDYLY': 'Randiwala Maha Vidyalaya',
}


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
