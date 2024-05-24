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


class GiveNutritionFact(Action):

    def name(self) -> Text:
        return "action_give_nutrition_fact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        df = pd.read_excel(r'D:\Study\Python\chatbot\testUnderthesea\excel\calo.xlsx')
        table = df.values.tolist()

        dispatcher.utter_message(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

        return []


class GiveNutrition(Action):

    def name(self) -> Text:
        return "action_give_nutrition"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        df = pd.read_excel(r'D:\Study\Python\chatbot\testUnderthesea\excel\calo.xlsx')
        table = df.values.tolist()

        slot_cust_food = tracker.get_slot("cust_food").lower()

        newtable = []
        for i in range(len(table)):
            if table[i][0].find(slot_cust_food) >= 0 or i == 0:
                a = []
                for j in range(len(table[i])):
                    a.append(table[i][j])
                newtable.append(a)

        dispatcher.utter_message(tabulate(newtable, headers="firstrow", tablefmt="fancy_grid"))

        return []


class GiveAdvise(Action):

    def name(self) -> Text:
        return "action_give_advise"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slot_cust_cond = tracker.get_slot("cust_cond").lower()
        slot_cust_role = tracker.get_slot("cust_role")
        slot_cust_name = tracker.get_slot("cust_name")
        rn = slot_cust_role + " " + slot_cust_name
        if slot_cust_cond in ("đau đầu", "nhức đầu", "đầu"):
            dispatcher.utter_message(rn + " có thế áp dụng một số phương pháp sau đây để làm giảm cơn đau hiệu quả:\n"
                                          "- Nghỉ ngơi, tránh căng thẳng\n- Uống nhiều nước\n- Chườm lạnh\n"
                                          "- Tắm nước nóng\n- Tập thể dục\n- Bấm huyệt, massage\n"
                                          "- Tránh xa tiếng ồn, nơi có ánh sáng gắt, gió to\n"
                                          "- Không nên ngồi máy tính quá lâu\n- Chế độ ăn uống hợp lý")
        elif slot_cust_cond in ("đau bụng", "bụng"):
            dispatcher.utter_message(rn + " có thế áp dụng một số phương pháp sau đây để làm giảm cơn đau hiệu quả:\n"
                                          "- Chườm ấm\n- Sử dụng baking soda\n- Nâng đầu lên cao để hết đau bụng\n"
                                          "- Ăn các món dễ tiêu hóa\n- nhờ bác sĩ kê đơn cho những loại thuốc bổ sung"
                                          " probiotic hoặc ăn nhiều thực phẩm lên men như sữa chua\n"
                                          "- Sử dụng thảo dược như: tiểu hồi, bạc hà, gừng "
                                          "- và hoa cúc, hoa cúc và gừng khô, ...\n"
                                          "- Massage nhẹ nhàng\n- Bổ sung lợi khuẩn mỗi ngày\n"
                                          "- Chế độ ăn uống hợp lý\n!!! Hãy đi khám bác sĩ nếu cơn đau không cải thiện "
                                          "hoặc khi có các triệu chứng nặng như: nôn ói, đại tiện ra máu, mệt mỏi, "
                                          "thiếu máu, ...")
        elif slot_cust_cond in ("sổ mũi", "nghẹt mũi"):
            dispatcher.utter_message(rn + " có thế áp dụng một số phương pháp sau để làm giảm sổ mũi hiệu quả:\n"
                                          "- Uống nhiều nước\n- Uống trà nóng\n- Xông hơi mặt\n- Tắm với nước ấm\n"
                                          "- Sử dụng dụng cụ rửa mũi\n- Ăn đồ cay để trị sổ mũi\n- Dùng capsaicin\n"
                                          "- Kê gối cao khi ngủ\n- Tăng độ ẩm không khí trong phòng hoặc trong nhà\n"
                                          "- Đeo khẩu trang\n!!! Đi khám bác sĩ nếu cơn đau không cải thiện hoặc khi"
                                          ": sốt cao trên 38 độ, đau cổ họng dữ dội, Đau nhức lồng ngực, khó thở hoặc "
                                          "thở khò khè, tình trạng sốt kéo dài liên tục, ...")
        elif slot_cust_cond in ("đau họng", "viêm họng"):
            dispatcher.utter_message(rn + " có thế áp dụng một số phương pháp sau đây để làm giảm cơn đau hiệu quả:\n"
                                          "- Súc miệng bằng nước muối\n- Sử dụng thuốc ngậm ho không kê đơn\n"
                                          "- Thử giảm đau OTC\n- Thưởng thức một giọt mật ong\n"
                                          "- Thử xịt họng có thành phần từ cây echinacea và xô thơm\n"
                                          "- Giữ đủ nước cho cơ thể\n- Sử dụng máy tạo độ ẩm\n- Tắm hơi\n"
                                          "!!! Hãy đi khám bác sĩ nếu cơn đau không cải thiện hoặc khi: bị đau dữ dội "
                                          "khi nuốt, phát sốt cao, buồn nôn hoặc nôn mửa, ...")
        elif slot_cust_cond in ("cảm", "sốt", "cảm cúm"):
            dispatcher.utter_message(rn + " có thế áp dụng một số phương pháp sau để làm giảm cơn cảm cúm hiệu quả:\n"
                                          "- Vệ sinh mũi sạch sẽ\n- Vệ sinh họng bằng nước muối loãng\n"
                                          "- Uống nhiều nước nóng\n- Chườm nóng hoặc chườm lạnh\n"
                                          "- Nghỉ ngơi, thư giãn\n- Uống thuốc hạ sốt\n- Xông lá\n- Ăn đồ nóng, lỏng\n"
                                          "- Sinh hoạt và nghỉ ngơi hợp lý\n!!! Bị cảm cúm thường có triệu chứng sốt, "
                                          "tuy nhiên sau 7 ngày vẫn không giảm sốt hoặc tái sốt thì bạn cần đến cơ "
                                          "sở y tế ngay vì có thể bị bội nhiễm vi khuẩn và các biến chứng nguy hiểm "
                                          "khó lường khác.")
        elif slot_cust_cond == "ho":
            dispatcher.utter_message(rn + " có thế sử dụng sau đây để làm giảm cơn ho hiệu quả:\n"
                                          "- Tỏi ngâm mật ong\n- Mật ong gừng\n- Chanh đào mật ong\n"
                                          "- Chanh sả mật ong\n- Lê hấp mật ong\n- Siro húng quất đường phèn\n"
                                          "- Hành tây ngâm mật ong\n- Quýt ngâm đường phèn\n!!! Hãy đi khám bác sĩ "
                                          "nếu cơn đau không cải thiện hoặc khi có các triệu chứng nặng như: ho khan "
                                          "không có dấu hiệu của cảm cúm hay viêm họng, tuy nhiên khi ngủ trưa hoặc "
                                          "ban đêm lại bị ho, ngứa họng và ho dai dẳng liên tục, ...")
        else:
            dispatcher.utter_message("a! hình như bệnh này Klee chưa được học "
                                     + slot_cust_role + " đợi Klee đi học đã nha!")

        return []


class GiveDrugstore(Action):

    def name(self) -> Text:
        return "action_give_drugstore"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        df = pd.read_excel(r'D:\Study\Python\chatbot\testUnderthesea\excel\quaythuoc.xlsx')
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

        location = soup.find("h1", class_="tt-news").text
        rawweather = soup.find("div", class_="content-news fix-content-news")
        weather = rawweather.text.replace("\n\n\n", "\n").replace("\n\n\n\n", "\n---------------------------\n")

        dispatcher.utter_message(location + "\n" + weather)

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

        df = pd.read_excel(r'D:\Study\Python\chatbot\testUnderthesea\excel\taptd.xlsx')
        table = df.values.tolist()

        dispatcher.utter_message(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

        return []
