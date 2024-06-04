# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import pandas as pd
import re


class WelcomWithName(Action):

    def name(self) -> Text:
        return "action_welcome_with_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slot_cust_role = tracker.get_slot("cust_role").lower()
        slot_cust_name = tracker.get_slot("cust_name")

        if slot_cust_role in ("tôi", "mình", "tớ", "tui", "t"):
            slot_cust_role = "bạn"
        if slot_cust_role not in ("anh", "chị", "cô", "bác", "chú", "dì", "tôi", "mình", "tớ", "tui", "t", "bạn"):
            slot_cust_role = "quý khách"
            dispatcher.utter_message("Klee rất hân hạnh được phục vụ " + slot_cust_role + " ạ!")
            return [SlotSet("cust_role", slot_cust_role)]
        dispatcher.utter_message("Klee rất hân hạnh được phục vụ " + slot_cust_role + " " + slot_cust_name + " ạ!")
        return [SlotSet("cust_role", slot_cust_role)]


class GiveNutrition(Action):

    def name(self) -> Text:
        return "action_give_nutrition"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Đọc file Excel đã được upload
        df = pd.read_excel(r'D:\Study\python\chatbot\Klee_TheHealthBot-master\excel\calo.xlsx')

        # Lấy giá trị từ slot "cust_food"
        slot_cust_food = tracker.get_slot("cust_food").lower()

        # Tìm kiếm các dòng có chứa từ khóa trong cột đầu tiên
        found_rows = df[df.iloc[:, 0].str.contains(slot_cust_food, case=False, na=False)]

        if not found_rows.empty:
            # Chọn dòng đầu tiên khớp với từ khóa
            first_row = found_rows.iloc[0]
            # Định dạng thông tin dinh dưỡng theo yêu cầu
            nutrition_info = f"[{first_row[1]}] {first_row[0]} có: {first_row[2]} CALO, {first_row[3]} ĐẠM (g), {first_row[4]} BÉO (g), {first_row[5]} CARB (g), {first_row[6]} ĐƯỜNG (g)"
            message = nutrition_info
        else:
            message = f"Không tìm thấy thông tin dinh dưỡng cho {slot_cust_food}."

        # Gửi tin nhắn đến người dùng
        dispatcher.utter_message(message)

        return []

class GiveDrugstore(Action):

    def name(self) -> Text:
        return "action_give_drugstore"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        df = pd.read_excel(r'D:\Study\python\chatbot\Klee_TheHealthBot-master\excel\quaythuoc.xlsx')
        table = df.values.tolist()

        dispatcher.utter_message(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

        return []


class GiveWeather(Action):

    def name(self) -> Text:
        return "action_give_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        resp = requests.get('https://nchmf.gov.vn/Kttvsite/vi-VN/1/hue-w7.html')
        soup = BeautifulSoup(resp.content, "html.parser")

        location = soup.find("h1", class_="tt-news").text.strip()
        rawweather = soup.find("div", class_="content-news fix-content-news")
        weather = rawweather.text.strip()

        # Clean and format the weather text
        weather = weather.replace("\n\n\n", "\n").replace("\n\n\n\n", "\n---------------------------\n")
        weather_lines = weather.split('\n')

        formatted_weather = []
        for line in weather_lines:
            line = line.strip()
            if line:
                if line.startswith("Nhiệt độ"):
                    line = "🌡️ " + line
                elif line.startswith("Độ ẩm"):
                    line = "💧 " + line
                elif line.startswith("Gió"):
                    line = "💨 " + line
                elif line.startswith("Mưa"):
                    line = "🌧️ " + line
                formatted_weather.append(line)

        formatted_weather_text = "\n".join(formatted_weather)

        message = f"📍 {location}\n\n{formatted_weather_text}"

        dispatcher.utter_message(message)

        return []


class GiveBMI(Action):

    def name(self) -> Text:
        return "action_give_bmi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slot_cust_height = tracker.get_slot("cust_height")
        slot_cust_weight = tracker.get_slot("cust_weight")
        slot_cust_role = tracker.get_slot("cust_role")

        height = ""
        x = re.findall('[0-9]+', slot_cust_height)
        if slot_cust_height.find("mét") == 0 or slot_cust_height.find("m") == 0:
            height += "1"
        for element in x:
            height += element
        height = int(height)
        if height < 20:
            height *= 10

        weight = ""
        x = re.findall('[0-9]+', slot_cust_weight)
        for element in x:
            weight += element
        weight = int(weight)

        bmi = weight / ((height/100)*(height/100))
        dispatcher.utter_message("Chỉ số BMI lý tưởng được các tổ chức y tế đưa ra là vào mức 18,5 - 25. "
                                 "Mỗi chỉ số BMI sẽ nói lên tình trạng cơ thể của chúng ta theo từng mức khác nhau.")
        dispatcher.utter_message("Chỉ số BMI của " + slot_cust_role + " là: " + str(bmi))

        tt = "Thể trạng của " + slot_cust_role
        if bmi < 18.5:
            dispatcher.utter_message(tt + ": Cân nặng thấp (gầy)")
        elif bmi < 24.9:
            dispatcher.utter_message(tt + ": Bình thường")
        elif bmi <= 25:
            dispatcher.utter_message(tt + ": Thừa cân")
        elif bmi < 30:
            dispatcher.utter_message(tt + ": Tiền béo phì")
        elif bmi < 35:
            dispatcher.utter_message(tt + ": Béo phì độ I")
        elif bmi < 40:
            dispatcher.utter_message(tt + ": Béo phì độ II")
        else:
            dispatcher.utter_message(tt + ": Béo phì độ III")
        return []


class GainWeight(Action):

    def name(self) -> Text:
        return "action_gain_weight"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Nạp nhiều calo là nguyên tắc cơ bản được áp dụng trong việc tăng cân. Khi muốn cơ "
                                 "thể tăng cân, điều đầu tiên một người cần làm là ăn nhiều hơn nhu cầu năng lượng "
                                 "hàng ngày cơ thể cần. Nếu nạp thêm 500 calo/ngày, những người gầy kinh niên có thể "
                                 "tăng thêm 0.5kg/tuần\n Một số cách tăng cân hiệu quả:\n"
                                 "- Nạp nhiều calo hơn lượng calo đã đốt cháy để tăng cân nhanh\n"
                                 "- Chú trọng bổ sung các thực phẩm giàu chất Protein\n"
                                 "- Tăng cường lượng carbohydrate và chất béo vào chế độ ăn tăng cân\n"
                                 "- Ăn 3 bữa chính và ít nhất 3 bữa phụ mỗi ngày giúp tăng cân nhanh\n"
                                 "- Duy trì chế độ ăn đều đặn 6 bữa/ngày\n"
                                 "- Tuyệt đối không bỏ bữa, đặc biệt bữa sáng\n"
                                 "- Ưu tiên thực phẩm lành mạnh, giàu năng lượng kết hợp nước xốt và gia vị\n"
                                 "- Uống các loại thức uống giàu calo\n"
                                 "- Ngủ đủ giấc mỗi ngày\n"
                                 "- Tập thể dục thể thao để để tăng cơ, tăng cân hiệu quả")

        return []


class LoseWeight(Action):

    def name(self) -> Text:
        return "action_lose_weight"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Cách giảm cân tốt nhất, đúng đắn nhất là cắt giảm lượng Calo cơ thể nạp vào. Có thể "
                                 "nói cân nặng là một phương trình cân bằng. Nếu ăn nhiều calo hơn mức đốt cháy, bạn "
                                 "sẽ tăng cân. Và nếu bạn ăn ít calo hơn và đốt cháy nhiều calo hơn thông qua hoạt "
                                 "động thể chất, bạn sẽ giảm cân.\n Một số cách giảm cân hiệu quả:\n"
                                 "- Kiểm soát năng lượng trong khẩu phần ăn\n"
                                 "- Cắt giảm lượng carbs tinh chế\n"
                                 "- Ăn đủ chất đạm, chất béo, rau củ quả là cách giảm cân lành mạnh nhất\n"
                                 "- Kết hợp với vận động, tập luyện\n"
                                 "- Ăn đủ bữa, đúng giờ, không bỏ bữa sáng\n"
                                 "- Ăn nhiều trái cây và rau\n"
                                 "- Uống nhiều nước, ăn thực phẩm nhiều chất xơ\n"
                                 "- Dùng bát, đĩa nhỏ hơn, lên kế hoạch cho bữa ăn\n"
                                 "- Không kiêng tuyệt đối bất kỳ loại thực phẩm nào\n"
                                 "- Không dự trữ đồ ăn vặt, cắt giảm rượu")

        return []


class Exercise(Action):

    def name(self) -> Text:
        return "action_exercise"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        df = pd.read_excel(r'D:\Study\python\chatbot\Klee_TheHealthBot-master\excel\taptd.xlsx')
        table = df.values.tolist()

        dispatcher.utter_message(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

        return []

# ViemPheQuanCap
class Chuan_doan_phanbiet_viemphequancap(Action):

    def name(self) -> Text:
        return "action_chuan_doan_phanbiet_viemphequancap"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # # slot_cust_role = tracker.get_slot("cust_role").lower()
        # # slot_cust_name = tracker.get_slot("cust_name")
        # if len(slot_cust_name) == 0:
        #     rn = slot_cust_role + slot_cust_name
        # else:
        #     rn = slot_cust_role + " " + slot_cust_name

        dispatcher.utter_message("Chẩn đoán phân biệt: \n"
                                 " - hen phế quản tăng tiết dịch: sau cơn hen thì hết các triệu chứng\n"
                                 " - ứ đọng phổi trong suy tim: có biểu hiện suy tim\n"
                                 " - nghe phổi có ran rít\n"
                                 " - Một số bệnh phổi có biểu hiện viêm phế quản: lao phổi, bệnh bụi phổi, ung thư phổi: "
                                 "không nghĩ đến viêm phế quản nếu triệu chứng nghe phổi chỉ ở một bên\n"
                                 )

        return []

    class Treatment_viemphequancap(Action):

        def name(self) -> Text:
            return "action_treatment_viemphequancap"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách chữa trị: \n"
                                     "Thể nhẹ: nghỉ ngơi tại giường, uống đủ nước, không cần dùng kháng sinh \n"
                                     "Thể nặng: Cho kháng sinh:\n"
                                     " - Nhóm Macrolid: Erythromycin uống 2g/ngày, Azythromycin 0.5 g/ngày đầu sau đó 250mg x 4 ngày, \n"
                                     " - Nhóm Quinolon: Ciprofloxacin uống 200 - 400mg/ ngày\n"
                                     " - Nên cho kháng histamin khi có dấu hiệu co thắt phế quản\n"
                                     " - Long đờm: Acemux, Mucomys 200 mg x 4 gói/ ngày\n"
                                     )

            return []


    class Prevent_viemphequancap(Action):

        def name(self) -> Text:
            return "action_prevent_viemphequancap"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách phòng bệnh: \n"
                                     " - Bỏ, hạn chế các yếu tố kích thích: thuốc lá thuốc lào \n"
                                     " - Bảo hộ lao động cho những người tiếp xúc với môi trường có nhiều bụi như công nhân làm việc ở hầm mỏ.\n"
                                     " - Xây dựng các xí nghiệp xa vùng dân cư và ngược chiều gió.\n"
                                     " - Tiêm phòng cúm vào mùa thu - đông\n"
                                     " - Điều trị tốt các ổ nhiễm trùng đường hô hấp trên"
                                     )

            return []

    class Treatment_tanghuyetap(Action):

        def name(self) -> Text:
            return "action_treatment_tanghuyetap"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách chữa trị: \n"
                                     " - Hạn chế Na dưới 5g NaCl mỗi ngày.\n"
                                     " - Hạn chế mỡ, các chất béo động vật\n"
                                     " - Không rượu, thuốc lá, chè đặc\n"
                                     " - Tránh lao động trí óc căng thẳng, lo lắng quá độ, nên tập thể dục nhẹ, đi bộ thư giãn, bơi lội\n"
                                     " - Giảm cân nặng\n"
                                     " - Hoạt động thể lực\n"
                                     )

            return []


    class Prevent_tanghuyetap(Action):

        def name(self) -> Text:
            return "action_prevent_tanghuyetap"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách phòng bệnh: \n"
                                     " - Tổ chức khám bệnh thường xuyên, có chu kỳ, có đo huyết áp, quan trọng nhất là phát hiện bệnh ở giai đoạn đầu\n"
                                     " - Bố trí giờ giấc, chế độ nghỉ ngơi hợp lý, xen kẽ\n"
                                     " - Hạn chế muối, tránh các chất kích thích (thuốc lá, cà phê, rượu, chè…..)\n"
                                     " - Trong sinh hoạt tránh mọi căng thẳng, xúc cảm mạnh.\n"
                                     " -  Những người lao động trí óc cần kết hợp với công việc chân tay nhẹ nhàng tập thể dục"
                                     )

            return []

    class Treatment_nhoimaucotim(Action):

        def name(self) -> Text:
            return "action_treatment_nhoimaucotim"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách chữa trị: \n"
                                     " Giai đoạn trước khi vào bệnh viện:\n"
                                     " - An thần Diazepam 10mg uống\n"
                                     " - Thuốc giãn mạch vành papaverin\n"
                                     " - Chuyển bệnh nhân đến bệnh viện\n"
                                     " Giai đoạn ở bệnh viện: \n"
                                     " - Thở oxy\n"
                                     " - Nitroglyxerin 0,5mg đặt dưới lưỡi\n"
                                     " - Nếu không hết đau cho propranolol 20mg (uống) x 2- 4 lần/ngày\n"
                                     " - Thuốc ức chế canxi: Nifedipin 10- 20mg x 3- 4 lần trong ngày\n"
                                     )

            return []

    class Prevent_nhoimaucotim(Action):

        def name(self) -> Text:
            return "action_prevent_nhoimaucotim"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách phòng bệnh: \n"
                                     " - Bỏ thuốc lá\n"
                                     " - Có chế độ theo dõi chặt chẽ huyết áp\n"
                                     " - Giảm mỡ máu\n"
                                     " - Điều trị tích cực đái tháo đường\n"
                                     " - Tăng cường luyện tập và hoạt động thể lực nhiều hơn\n"
                                     )

            return []

    class Treatment_sogan(Action):

        def name(self) -> Text:
            return "action_treatment_sogan"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách chữa trị: \n"
                                     " Chế độ nghỉ ngơi tuyệt đối trong đợt tiến triển\n"
                                     " Ăn tăng đường, đạm, ăn nhạt nếu có phù\n"
                                     " Thuốc: \n"
                                     " - Cải thiện chuyển hoá tế bào gan: các vitamin\n"
                                     " - Tăng cường đồng hoá đạm: Testosteron 100mg/ 2 tuần\n"
                                     " - Uống, truyền Glucoza\n"
                                     " - Truyền máu, đạm, plasma, albumin.\n"
                                     " - Lợi tiểu không thải Kali, kháng aldosteron;"
                                     )

            return []

    class Prevent_sogan(Action):

        def name(self) -> Text:
            return "action_prevent_sogan"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách phòng bệnh: \n"
                                     " - Biện pháp chung dự phòng là không làm cho gan nhiễm độc.Điều trị các bệnh gan có sẵn\n"
                                     " - Không uống nhiều rượu\n"
                                     " - p tuyên truyền tác hại của rượu , bệnh viêm gan B , các tác nhân khác... và dự phòng Vaccin viêm gan B\n"
                                     )

            return []

    class Treatment_daithaoduong(Action):

        def name(self) -> Text:
            return "action_treatment_daithaoduong"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách chữa trị: \n"
                                     " - Đái tháo đường typ I: Thường ở người trẻ:\n"
                                     "thể trạng gầy, có nhiều biến chứng và hay "
                                     "gặp biến chứng về chuyển hoá, kháng nguyên bạch cầu thuộc nhóm HLA-DR3, "
                                     "HLA-DR4, có kháng thể chống tế bào Langerhgans. Bắt buộc phải điều trị bằng"
                                     "insulin tiêm. - \n"
                                     " - Đái tháo đường typ II: Thường ở người nhiều tuổi, thể trạng béo, ít có biến "
                                     "chứng và hay gặp biến chứng về tim mạch. Thường dùng viên hạ đường huyết uống,"
                                     "trong một số trường hợp cụ thể (hôn mê, có biến chứng tim mạch, giai đoạn muộn) "
                                     "phải dùng insulin tiêm.\n"
                                     )

            return []

    class Prevent_daithaoduong(Action):

        def name(self) -> Text:
            return "action_prevent_daithaoduong"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách phòng bệnh: \n"
                                     " - Nghỉ ngơi hoàn toàn trong giai đoạn cấp\n"
                                     " - Giai đoạn ổn định, làm việc bình thường, tránh lao động quá sức\n"
                                     " - Ăn: Hạn chế chất Glucid nhưng vẫn phải đảm bảo số calo cần thiết cho mỗi ngày (2000 calo)\n"
                                     " - Điều chỉnh lượng thức ăn theo kết quả xét nghiệm sinh hóa cho thích hợp\n"
                                     " - Ăn tăng Protid thực vật và nhiều Vitamin"
                                     )

            return []

    class Treatment_loetdaday(Action):

        def name(self) -> Text:
            return "action_treatment_loetdaday"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách chữa trị: \n"
                                     " - Thuốc chống axit: Chủ yếu trung hoà axit: Hydroxit nhôm, Hydroxit magiê, trixilicat magiê. "
                                     "Không dùng NaHCO3 gây viêm dạ dày và tăng HCl pha 2 \n"
                                     " - Các thuốc bảo vệ niêm mạc, băng niêm mạc: Alumin Sacharo sulfat ( Surcralfate). Khi gặp HCl "
                                     "trở nên dính quánh, có tác dụng băng niêm mạc\n"
                                     " - Các thuốc chống bài tiết: Ức chế cảm thụ H2 (tế bào viền): cimetidin, ranitidin, nizatidin, "
                                     "famotidin thế hệ sau có nhiều ưu việt hơn thế hệ trước liều nhỏ hơn ít tác dụng phụ hơn\n"
                                     " - \n"
                                     )

            return []

    class Prevent_loetdaday(Action):

        def name(self) -> Text:
            return "action_prevent_loetdaday"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách phòng bệnh: \n"
                                     " - Điều trị sớm bệnh loét, điều trị triệt để, tránh các biến chứng xảy ra\n"
                                     " - Một số thuốc có khả năng làm tăng nguy cơ biến chứng hoặc tăng nguy cơ "
                                     "mắc bệnh như các thuốc giảm đau chống viêm, các steroid phẩi được chú ý đặc biêt "
                                     "khi dùng cho nhưngbnguoi có tiền sử loét\n"
                                     " - Các thuốc điều trị dạ dày hành tá tràng hiện nay chưa thấy có tai biến đáng kể. "
                                     "với các kháng sinh phải tuân thủ nguyên tắc sử dụng klháng sinh.\n"
                                     )

            return []

    class Treatment_benh(Action):

        def name(self) -> Text:
            return "action_treatment_soithan"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách chữa trị:\n"
                                     " - Chú ý chế độ ăn: ăn nhiều hoa quả, rau, sữa. Nên hạn chế ăn thịt "
                                     "hay thức ăn có nhiều Canxi (tuỳ theo loại sỏi)\n"
                                     " - Dùng từng đợt thuốc lợi tiểu đông và tây y.\n"
                                     " - Dùng kết hợp với thuốc tăng co bóp mạch như Prostigmin hoặc thuốc có tác "
                                     "dụng giãn cơ như Atropin hay Nospa\n"
                                     " - Dùng kháng sinh trong những trường hợp có nhiễm khuẩn\n"
                                     )

            return []

    class Prevent_benh(Action):

        def name(self) -> Text:
            return "action_prevent_soithan"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message("Sau đây là một số cách phòng bệnh: \n"
                                     " - Cần tẩy giun, sán thường xuyên để tránh những rối loạn và chuyển hoá chất.\n"
                                     " - Đảm bảo chế độ ăn đủ các chất , hợp lý, thức ăn nên thay đổi.\n"
                                     " - Cho uống đủ nước với những bệnh nhân phải nằm lâu dài (liệt tuỷ, lao cột sống, gãy xương).\n"
                                     )

            return []