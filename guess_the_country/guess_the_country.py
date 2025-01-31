import random
import time
import emoji

from game import Game


class GuessTheCountry(Game):
    # Class-level variable to track all countries shown across all players
    already_shown_countries = set()

    def __init__(self):

        # All 195 countries with emoji hints
        # Dictionary of all 195 countries with emoji clues
        self.countries =  {
            "🇦🇫🏔️🕌": "afghanistan", "🇦🇱⛰️🏛️": "albania", "🇩🇿🏜️🕌": "algeria",
            "🇦🇩🏔️🏰": "andorra", "🇦🇴🦏🛢️": "angola", "🇦🇬🏝️🎭": "antigua and barbuda",
            "🇦🇷🥩⚽": "argentina", "🇦🇲⛪⛰️": "armenia", "🇦🇺🐨🏄": "australia",
            "🇦🇹🎼🏰": "austria", "🇦🇿🔥🕌": "azerbaijan", "🇧🇸🏝️🌊": "bahamas",
            "🇧🇭🏝️🏎️": "bahrain", "🇧🇩🐅🌾": "bangladesh", "🇧🇧🏝️🎶": "barbados",
            "🇧🇾🏰🛤️": "belarus", "🇧🇪🍫🏰": "belgium", "🇧🇿🌊🐠": "belize",
            "🇧🇯🏜️🕌": "benin", "🇧🇹🗻🙏": "bhutan", "🇧🇴⛰️🏞️": "bolivia",
            "🇧🇦🏰🎶": "bosnia and herzegovina", "🇧🇼🦁🏜️": "botswana",
            "🇧🇷🏖️⚽": "brazil", "🇧🇳🕌🏝️": "brunei", "🇧🇬🏛️🎶": "bulgaria",
            "🇧🇫🏜️🏰": "burkina faso", "🇧🇮⛰️🌊": "burundi", "🇨🇻🏝️🌊": "cape verde",
            "🇨🇲🐘🏜️": "cameroon", "🇨🇦🍁🏒": "canada", "🇨🇫🐘🌳": "central african republic",
            "🇨🇱🏔️🍷": "chile", "🇨🇳🏯🐉": "china", "🇨🇴☕🏔️": "colombia",
            "🇨🇩🌳🐘": "democratic republic of the congo", "🇨🇷🏝️🌋": "costa rica",
            "🇨🇮🏝️🏜️": "ivory coast", "🇭🇷🏰🌊": "croatia", "🇨🇺🕺🚬": "cuba",
            "🇨🇾🏛️🌞": "cyprus", "🇨🇿🍺🏰": "czech republic", "🇩🇰🛳️🏰": "denmark",
            "🇪🇨🌋🐢": "ecuador", "🇪🇬🏺🐪": "egypt", "🇸🇻🌋🏝️": "el salvador",
            "🇪🇪🏰🎼": "estonia", "🇫🇯🏝️🐠": "fiji", "🇫🇮🌲🎼": "finland",
            "🇫🇷🗼🥖": "france", "🇩🇪🍺🏰": "germany", "🇬🇭🏝️🎶": "ghana",
            "🇬🇷🏛️🏺": "greece", "🇬🇹🏛️🌋": "guatemala", "🇭🇳🏔️🏝️": "honduras",
            "🇮🇳🕌🐘": "india", "🇮🇩🏝️🌋": "indonesia", "🇮🇷🏛️🕌": "iran",
            "🇮🇶🕌🏜️": "iraq", "🇮🇪☘️🍺": "ireland", "🇮🇹🍕🏛️": "italy",
            "🇯🇲🏝️🎶": "jamaica", "🇯🇵⛩️🍣": "japan", "🇯🇴🏜️🏛️": "jordan",
            "🇰🇪🦒🏜️": "kenya", "🇰🇷🎮🏯": "south korea", "🇰🇵🏯🚀": "north korea",
            "🇱🇦🌿🛶": "laos", "🇱🇧🕌🏛️": "lebanon", "🇱🇾🏜️🛢️": "libya",
            "🇲🇾🏝️🍜": "malaysia", "🇲🇽🌮🕌": "mexico", "🇲🇦🏜️🐪": "morocco",
            "🇲🇳🏜️🐴": "mongolia", "🇲🇿🏖️🐠": "mozambique", "🇳🇵🏔️🙏": "nepal",
            "🇳🇱🌷🏰": "netherlands", "🇳🇬🛢️🎶": "nigeria", "🇳🇴🏔️🎿": "norway",
            "🇵🇰🕌🏔️": "pakistan", "🇵🇪🏔️🏛️": "peru", "🇵🇭🏝️🍍": "philippines",
            "🇵🇹🏰⚽": "portugal", "🇶🇦🏜️🏗️": "qatar", "🇷🇴🏛️🏰": "romania",
            "🇷🇺🏰🐻": "russia", "🇷🇼🏞️🦓": "rwanda", "🇸🇦🕌🏜️": "saudi arabia",
            "🇸🇬🏙️🌴": "singapore", "🇪🇸🏰🍷": "spain", "🇱🇰🐘🏝️": "sri lanka",
            "🇸🇪🏔️🎿": "sweden", "🇨🇭🏔️🍫": "switzerland", "🇹🇭🏝️🍜": "thailand",
            "🇹🇷🏛️🥙": "turkey", "🇬🇧👑☕": "united kingdom", "🇺🇸🗽🍔": "usa",
            "🇿🇦🦁🏜️": "south africa", "🇻🇳🌿🍜": "vietnam", "🇿🇲🦓🏞️": "zambia"
        }
        # self.countries ={
        #     emoji.emojize(":flag_af:"): "Afghanistan", emoji.emojize(":flag_al:"): "Albania", emoji.emojize(":flag_dz:"): "Algeria", 
        #     emoji.emojize(":flag_as:"): "American Samoa", emoji.emojize(":flag_ad:"): "Andorra", emoji.emojize(":flag_ao:"): "Angola", 
        #     emoji.emojize(":flag_ai:"): "Anguilla", emoji.emojize(":flag_ag:"): "Antigua and Barbuda", emoji.emojize(":flag_ar:"): "Argentina", 
        #     emoji.emojize(":flag_am:"): "Armenia", emoji.emojize(":flag_aw:"): "Aruba", emoji.emojize(":flag_au:"): "Australia", 
        #     emoji.emojize(":flag_at:"): "Austria", emoji.emojize(":flag_az:"): "Azerbaijan", emoji.emojize(":flag_bs:"): "Bahamas", 
        #     emoji.emojize(":flag_bh:"): "Bahrain", emoji.emojize(":flag_bd:"): "Bangladesh", emoji.emojize(":flag_bb:"): "Barbados", 
        #     emoji.emojize(":flag_by:"): "Belarus", emoji.emojize(":flag_be:"): "Belgium", emoji.emojize(":flag_bz:"): "Belize", 
        #     emoji.emojize(":flag_bj:"): "Benin", emoji.emojize(":flag_bm:"): "Bermuda", emoji.emojize(":flag_bt:"): "Bhutan", 
        #     emoji.emojize(":flag_bo:"): "Bolivia", emoji.emojize(":flag_ba:"): "Bosnia and Herzegovina", emoji.emojize(":flag_bw:"): "Botswana", 
        #     emoji.emojize(":flag_br:"): "Brazil", emoji.emojize(":flag_io:"): "British Indian Ocean Territory", emoji.emojize(":flag_bn:"): "Brunei", 
        #     emoji.emojize(":flag_bg:"): "Bulgaria", emoji.emojize(":flag_bf:"): "Burkina Faso", emoji.emojize(":flag_bi:"): "Burundi", 
        #     emoji.emojize(":flag_kh:"): "Cambodia", emoji.emojize(":flag_cm:"): "Cameroon", emoji.emojize(":flag_ca:"): "Canada", 
        #     emoji.emojize(":flag_cv:"): "Cape Verde", emoji.emojize(":flag_ky:"): "Cayman Islands", emoji.emojize(":flag_cf:"): "Central African Republic", 
        #     emoji.emojize(":flag_td:"): "Chad", emoji.emojize(":flag_cl:"): "Chile", emoji.emojize(":flag_cn:"): "China", 
        #     emoji.emojize(":flag_co:"): "Colombia", emoji.emojize(":flag_km:"): "Comoros", emoji.emojize(":flag_cd:"): "Congo (Congo-Brazzaville)", 
        #     emoji.emojize(":flag_cg:"): "Congo (Congo-Kinshasa)", emoji.emojize(":flag_ck:"): "Cook Islands", emoji.emojize(":flag_cr:"): "Costa Rica", 
        #     emoji.emojize(":flag_hr:"): "Croatia", emoji.emojize(":flag_cu:"): "Cuba", emoji.emojize(":flag_cy:"): "Cyprus", 
        #     emoji.emojize(":flag_cz:"): "Czechia", emoji.emojize(":flag_dk:"): "Denmark", emoji.emojize(":flag_dj:"): "Djibouti", 
        #     emoji.emojize(":flag_dm:"): "Dominica", emoji.emojize(":flag_do:"): "Dominican Republic", emoji.emojize(":flag_ec:"): "Ecuador", 
        #     emoji.emojize(":flag_eg:"): "Egypt", emoji.emojize(":flag_sv:"): "El Salvador", emoji.emojize(":flag_gq:"): "Equatorial Guinea", 
        #     emoji.emojize(":flag_er:"): "Eritrea", emoji.emojize(":flag_ee:"): "Estonia", emoji.emojize(":flag_et:"): "Ethiopia", 
        #     emoji.emojize(":flag_fk:"): "Falkland Islands", emoji.emojize(":flag_fo:"): "Faroe Islands", emoji.emojize(":flag_fj:"): "Fiji", 
        #     emoji.emojize(":flag_fi:"): "Finland", emoji.emojize(":flag_fr:"): "France", emoji.emojize(":flag_gf:"): "French Guiana", 
        #     emoji.emojize(":flag_pf:"): "French Polynesia", emoji.emojize(":flag_ga:"): "Gabon", emoji.emojize(":flag_gm:"): "Gambia", 
        #     emoji.emojize(":flag_ge:"): "Georgia", emoji.emojize(":flag_de:"): "Germany", emoji.emojize(":flag_gh:"): "Ghana", 
        #     emoji.emojize(":flag_gr:"): "Greece", emoji.emojize(":flag_gl:"): "Greenland", emoji.emojize(":flag_gd:"): "Grenada", 
        #     emoji.emojize(":flag_gp:"): "Guadeloupe", emoji.emojize(":flag_gu:"): "Guam", emoji.emojize(":flag_gt:"): "Guatemala", 
        #     emoji.emojize(":flag_gn:"): "Guinea", emoji.emojize(":flag_gw:"): "Guinea-Bissau", emoji.emojize(":flag_gy:"): "Guyana", 
        #     emoji.emojize(":flag_ht:"): "Haiti", emoji.emojize(":flag_hn:"): "Honduras", emoji.emojize(":flag_hk:"): "Hong Kong", 
        #     emoji.emojize(":flag_hu:"): "Hungary", emoji.emojize(":flag_is:"): "Iceland", emoji.emojize(":flag_in:"): "India", 
        #     emoji.emojize(":flag_id:"): "Indonesia", emoji.emojize(":flag_ir:"): "Iran", emoji.emojize(":flag_iq:"): "Iraq", 
        #     emoji.emojize(":flag_ie:"): "Ireland", emoji.emojize(":flag_il:"): "Israel", emoji.emojize(":flag_it:"): "Italy", 
        #     emoji.emojize(":flag_ci:"): "Ivory Coast", emoji.emojize(":flag_jm:"): "Jamaica", emoji.emojize(":flag_jp:"): "Japan", 
        #     emoji.emojize(":flag_jo:"): "Jordan", emoji.emojize(":flag_kz:"): "Kazakhstan", emoji.emojize(":flag_ke:"): "Kenya", 
        #     emoji.emojize(":flag_ki:"): "Kiribati", emoji.emojize(":flag_kp:"): "North Korea", emoji.emojize(":flag_kr:"): "South Korea", 
        #     emoji.emojize(":flag_kw:"): "Kuwait", emoji.emojize(":flag_kg:"): "Kyrgyzstan", emoji.emojize(":flag_la:"): "Laos", 
        #     emoji.emojize(":flag_lv:"): "Latvia", emoji.emojize(":flag_lb:"): "Lebanon", emoji.emojize(":flag_ls:"): "Lesotho", 
        #     emoji.emojize(":flag_lr:"): "Liberia", emoji.emojize(":flag_li:"): "Liechtenstein", emoji.emojize(":flag_lt:"): "Lithuania", 
        #     emoji.emojize(":flag_lu:"): "Luxembourg", emoji.emojize(":flag_mk:"): "North Macedonia", emoji.emojize(":flag_mg:"): "Madagascar", 
        #     emoji.emojize(":flag_my:"): "Malaysia", emoji.emojize(":flag_mv:"): "Maldives", emoji.emojize(":flag_ml:"): "Mali", 
        #     emoji.emojize(":flag_mt:"): "Malta", emoji.emojize(":flag_mh:"): "Marshall Islands", emoji.emojize(":flag_mq:"): "Martinique", 
        #     emoji.emojize(":flag_mr:"): "Mauritania", emoji.emojize(":flag_mu:"): "Mauritius", emoji.emojize(":flag_yu:"): "Yugoslavia", 
        #     emoji.emojize(":flag_mx:"): "Mexico", emoji.emojize(":flag_fm:"): "Micronesia", emoji.emojize(":flag_md:"): "Moldova", 
        #     emoji.emojize(":flag_mc:"): "Monaco", emoji.emojize(":flag_mn:"): "Mongolia", emoji.emojize(":flag_me:"): "Montenegro", 
        #     emoji.emojize(":flag_ms:"): "Montserrat", emoji.emojize(":flag_ma:"): "Morocco", emoji.emojize(":flag_mz:"): "Mozambique", 
        #     emoji.emojize(":flag_mm:"): "Myanmar", emoji.emojize(":flag_na:"): "Namibia", emoji.emojize(":flag_nr:"): "Nauru", 
        #     emoji.emojize(":flag_np:"): "Nepal", emoji.emojize(":flag_nl:"): "Netherlands", emoji.emojize(":flag_nc:"): "New Caledonia", 
        #     emoji.emojize(":flag_nz:"): "New Zealand", emoji.emojize(":flag_ni:"): "Nicaragua", emoji.emojize(":flag_ne:"): "Niger", 
        #     emoji.emojize(":flag_ng:"): "Nigeria", emoji.emojize(":flag_no:"): "Norway", emoji.emojize(":flag_om:"): "Oman", 
        #     emoji.emojize(":flag_pk:"): "Pakistan", emoji.emojize(":flag_pw:"): "Palau", emoji.emojize(":flag_pa:"): "Panama", 
        #     emoji.emojize(":flag_pg:"): "Papua New Guinea", emoji.emojize(":flag_py:"): "Paraguay", emoji.emojize(":flag_pe:"): "Peru", 
        #     emoji.emojize(":flag_ph:"): "Philippines", emoji.emojize(":flag_pl:"): "Poland", emoji.emojize(":flag_pt:"): "Portugal", 
        #     emoji.emojize(":flag_pr:"): "Puerto Rico", emoji.emojize(":flag_qa:"): "Qatar", emoji.emojize(":flag_re:"): "Reunion", 
        #     emoji.emojize(":flag_ro:"): "Romania", emoji.emojize(":flag_ru:"): "Russia", emoji.emojize(":flag_rw:"): "Rwanda", 
        #     emoji.emojize(":flag_sa:"): "Saudi Arabia", emoji.emojize(":flag_rs:"): "Serbia", emoji.emojize(":flag_sc:"): "Seychelles", 
        #     emoji.emojize(":flag_sl:"): "Sierra Leone", emoji.emojize(":flag_sg:"): "Singapore", emoji.emojize(":flag_sk:"): "Slovakia", 
        #     emoji.emojize(":flag_si:"): "Slovenia", emoji.emojize(":flag_sb:"): "Solomon Islands", emoji.emojize(":flag_so:"): "Somalia", 
        #     emoji.emojize(":flag_za:"): "South Africa", emoji.emojize(":flag_es:"): "Spain", emoji.emojize(":flag_lk:"): "Sri Lanka", 
        #     emoji.emojize(":flag_sd:"): "Sudan", emoji.emojize(":flag_sr:"): "Suriname", emoji.emojize(":flag_sj:"): "Svalbard and Jan Mayen", 
        #     emoji.emojize(":flag_sz:"): "Swaziland", emoji.emojize(":flag_se:"): "Sweden", emoji.emojize(":flag_ch:"): "Switzerland", 
        #     emoji.emojize(":flag_sy:"): "Syria", emoji.emojize(":flag_tw:"): "Taiwan", emoji.emojize(":flag_tj:"): "Tajikistan", 
        #     emoji.emojize(":flag_tz:"): "Tanzania", emoji.emojize(":flag_th:"): "Thailand", emoji.emojize(":flag_tl:"): "Timor-Leste", 
        #     emoji.emojize(":flag_tg:"): "Togo", emoji.emojize(":flag_to:"): "Tonga", emoji.emojize(":flag_tt:"): "Trinidad and Tobago", 
        #     emoji.emojize(":flag_tn:"): "Tunisia", emoji.emojize(":flag_tr:"): "Turkey", emoji.emojize(":flag_tm:"): "Turkmenistan", 
        #     emoji.emojize(":flag_tc:"): "Turks and Caicos Islands", emoji.emojize(":flag_tv:"): "Tuvalu", emoji.emojize(":flag_ug:"): "Uganda", 
        #     emoji.emojize(":flag_ua:"): "Ukraine", emoji.emojize(":flag_ae:"): "United Arab Emirates", emoji.emojize(":flag_gb:"): "United Kingdom", 
        #     emoji.emojize(":flag_us:"): "United States", emoji.emojize(":flag_uy:"): "Uruguay", emoji.emojize(":flag_uz:"): "Uzbekistan", 
        #     emoji.emojize(":flag_vu:"): "Vanuatu", emoji.emojize(":flag_va:"): "Vatican City", emoji.emojize(":flag_ve:"): "Venezuela", 
        #     emoji.emojize(":flag_vn:"): "Vietnam", emoji.emojize(":flag_wf:"): "Wallis and Futuna", emoji.emojize(":flag_ye:"): "Yemen", 
        #     emoji.emojize(":flag_zm:"): "Zambia", emoji.emojize(":flag_zw:"): "Zimbabwe"
        # }
        self.lifelines = {"hint": True, "fifty_fifty": True, "skip": True}
        self.round_earnings = 0
        self.start_time = time.time()
        self.game_time_limit = 10 * 60  # 10 minutes
        self.selected_countries = []
        self.safety_points = [400, 600, 800]
        self.earnings = 0
        self.rounds = 5
        self.timer = 10 * 60  # 10 minutes in seconds

    def name(self):
        return "Guess The Country"

    def reset_game(self):
        self.lifelines = {"hint": True, "fifty_fifty": True, "skip": True}
        self.round_earnings = 0
    def show_earnings(self):
        print(f"Total earnings this round: {self.earnings} Naira")

    def apply_safety(self):
        # Check the round_earnings and apply the safety thresholds
        if self.round_earnings < 400:
            print("😢 You lost all your earnings!")
            self.round_earnings = 0
        elif self.round_earnings < 600:
            print(f"💰 You keep ₦400 (Safety Point).")
            self.round_earnings = 400
        elif self.round_earnings < 800:
            print(f"💰 You keep ₦600 (Safety Point).")
            self.round_earnings = 600
        elif self.round_earnings < 900:
            print(f"💰 You keep ₦800 (Safety Point).")
            self.round_earnings = 800
        else:
            print(f"🎉 You reached the maximum safety point of ₦800!")
            self.round_earnings = 800

    def play_round(self, round_num):
        # Start the timer for each round
        round_timer = self.timer
        round_earnings = 0
        safety_triggered = False

        while True:
            if round_timer <= 0:
                print("Time's up! You failed to complete the round.")
                break

            country, country_name = self.get_random_country()

            if country is None:
                print("No more countries available!")
                break

            print(f"Identify the country: {country}")
            print("You have 4 options: (1) Answer (2) Use Hint (3) Use 50/50 (4) Double Bonus Round (5) Forfeit")

            # Timer countdown
            print(f"Time remaining: {round_timer // 60} minutes and {round_timer % 60} seconds")
            user_input = input("What do you want to do? ")
            while True:
                if user_input not in ['1', '2', '3', '4', '5']:
                    print("Invalid input! Please enter a valid option.")
                    user_input = input("What do you want to do? ")
                else:
                    break
            if user_input == '1':  # Answer
                answer = input("Enter your guess: ")
                if answer.lower() == country_name.lower():
                    print("Correct! You earn 200 Naira!")
                    round_earnings += 200
                    self.earnings += 200
                else:
                    print("Wrong answer! You failed this round.")
                    if round_earnings >= 800:
                        self.earnings = 800
                    elif round_earnings >= 600:
                        self.earnings = 600
                    elif round_earnings >= 400:
                        self.earnings = 400
                    else:
                        self.earnings = 0
                    self.show_earnings()
                    return  # End round if user fails
            elif user_input == '2':  # Use hint
                print(f"Hint: The country starts with {country_name[0]}")
                round_timer -= 30  # Use 30 seconds for hint
            elif user_input == '3':  # Use 50/50
                print("Using 50/50 lifeline...")
                # In this case, we will simulate a 50/50 scenario by removing two incorrect options.
                incorrect_country = random.choice([name for name in self.countries.values() if name != country_name])
                print(f"Remaining options: {country_name} and {incorrect_country}")
                round_timer -= 30  # Use 30 seconds for the 50/50 lifeline

            elif user_input == '4':  # Double bonus round
                print("Double Bonus! You will earn double for this round!")
                round_earnings *= 2  # Double the earnings for this round
                round_timer -= 60  # Spend 1 minute on the bonus round

            elif user_input == '5':  # Forfeit
                print("You chose to forfeit the game.")
                self.show_earnings()
                return  # End the game immediately on forfeit

            # Decrease timer by 1 minute for each iteration (simulate turn taking)
            round_timer -= 60
            if round_earnings >= self.safety_points[2]:
                print(f"Safety point reached! You walk away with {self.earnings} Naira!")
                break
            elif round_earnings >= self.safety_points[1]:
                print(f"Safety point reached! You walk away with {self.earnings} Naira!")
                break
            elif round_earnings >= self.safety_points[0]:
                print(f"Safety point reached! You walk away with {self.earnings} Naira!")
                break
    
    def get_random_country(self):
        available_countries = list(self.countries.items())
        random.shuffle(available_countries)

        for country, country_name in available_countries:
            if country not in self.selected_countries:
                self.selected_countries.append(country)
                return country, country_name

        return None, None  # If no countries left
    
    def play(self):
        round_num = 1
        while round_num <= self.rounds and self.countries:
            print(f"\nRound {round_num}:")
            self.play_round(round_num)
            round_num += 1
