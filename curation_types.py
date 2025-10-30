import os
import json
from typing import Literal
from openai import OpenAI

# 작품명 리스트 (10개 작품)
ARTWORK_NAMES = [
    "프리마베라",
    "비너스의 탄생",
    "파리스의 심판",
    "아담의 창조",
    "최후의 만찬",
    "성 마태를 부르심",
    "아테네 학당",
    "회화의 기술",
    "시녀들",
    "야경"
]

# 한국어-영어 작품명 매핑
ARTWORK_NAME_KR_TO_EN = {
    "프리마베라": "Primavera",
    "비너스의 탄생": "The Birth of Venus",
    "파리스의 심판": "The Judgment of Paris",
    "아담의 창조": "The Creation of Adam",
    "최후의 만찬": "The Last Supper",
    "성 마태를 부르심": "The Calling of Saint Matthew",
    "아테네 학당": "The School of Athens",
    "회화의 기술": "The Art of Painting",
    "시녀들": "Las Meninas",
    "야경": "The Night Watch"
}

# 작품명 타입 정의
ArtworkName = Literal[
    "프리마베라",
    "비너스의 탄생",
    "파리스의 심판",
    "아담의 창조",
    "최후의 만찬",
    "성 마태를 부르심",
    "아테네 학당",
    "회화의 기술",
    "시녀들",
    "야경"
]


class CurationTypes:
    """
    미술관 큐레이션 NPC의 다양한 발화 타입을 제공하는 클래스.
    6가지 큐레이션 타입에 따라 다른 방식의 나레이션을 생성합니다.
    """
    
    def __init__(self, api_key=None, comparison_data_path="assets/llm/transformed_pair.json", prompts_dir="prompts"):
        """
        CurationTypes 클래스를 초기화합니다.
        
        :param api_key: OpenAI API 키. None이면 환경 변수에서 찾습니다.
        :param comparison_data_path: 작품 비교 데이터 JSON 파일 경로
        :param prompts_dir: 프롬프트 파일들이 있는 디렉토리 경로
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "OpenAI API 키가 설정되지 않았습니다. "
                "환경 변수 OPENAI_API_KEY를 설정하거나 api_key 파라미터를 전달하세요."
            )
        
        self.client = OpenAI(api_key=api_key)
        self.prompts_dir = prompts_dir
        
        # 작품 비교 데이터 로드
        self.comparison_data = {}
        try:
            with open(comparison_data_path, 'r', encoding='utf-8') as f:
                self.comparison_data = json.load(f)
        except FileNotFoundError:
            print(f"경고: 비교 데이터 파일을 찾을 수 없습니다: {comparison_data_path}")
        except json.JSONDecodeError:
            print(f"경고: 비교 데이터 파일을 읽을 수 없습니다: {comparison_data_path}")
    
    def _load_prompt(self, filename):
        """
        프롬프트 파일을 읽어오는 내부 메서드
        
        :param filename: 프롬프트 파일명 (예: "prompt_1.txt")
        :return: 프롬프트 문자열
        """
        filepath = os.path.join(self.prompts_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {filepath}")
    
    def _get_llm_response(self, prompt):
        """
        OpenAI API를 호출하여 응답을 반환하는 내부 메서드
        
        :param prompt: LLM에 전달할 프롬프트
        :return: LLM 응답 문자열
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def _get_comparison_data(self, art_name, related_artwork):
        """
        두 작품의 비교 데이터를 가져오는 내부 메서드
        
        :param art_name: 현재 작품명
        :param related_artwork: 비교할 작품명
        :return: 공통점과 차이점 문자열, 없으면 None
        """
        # 두 가지 키 형식 시도 (순서가 바뀔 수 있음)
        key1 = f"{art_name}-{related_artwork}"
        key2 = f"{related_artwork}-{art_name}"
        
        if key1 in self.comparison_data:
            return self.comparison_data[key1]
        elif key2 in self.comparison_data:
            return self.comparison_data[key2]
        else:
            return None
    
    def _get_question_answer(self, art_name, question, memory=""):
        """
        사용자 질문에 대한 간단한 답변을 생성하는 헬퍼 메서드
        
        :param art_name: 작품명
        :param question: 사용자 질문
        :param memory: 이전 대화 기록
        :return: 간단한 답변 문자열 (1문장)
        """
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        memory_section = ""
        if memory:
            memory_section = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용을 참고하여 답변하되, 중복을 피하세요."
        
        prompt_template = self._load_prompt("prompt_question_answer.txt")
        prompt = prompt_template.format(
            art_name=art_name,
            art_name_en=art_name_en,
            question=question,
            memory_section=memory_section
        )
        return self._get_llm_response(prompt)
    
    def curation_type_1(self, art_name, memory="", viewed_artworks=None, question=None):
        """
        큐레이션 타입 1: 작품 설명의 핵심 맥락 제공
        작품의 핵심 주제와 맥락을 120~170자로 간결하게 설명합니다.
        """
        # 질문이 있으면 먼저 간단히 답변
        question_answer = ""
        if question:
            question_answer = self._get_question_answer(art_name, question, memory)
        
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        memory_section = ""
        if memory:
            memory_section = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 관점을 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt_template = self._load_prompt("prompt_1.txt")
        prompt = prompt_template.format(
            art_name=art_name,
            art_name_en=art_name_en,
            memory_section=memory_section
        )
        main_response = self._get_llm_response(prompt)
        
        # 질문 답변이 있으면 연결해서 반환
        if question_answer:
            return f"{question_answer} {main_response}"
        return main_response
    
    def curation_type_2(self, art_name, question=None, memory="", viewed_artworks=None):
        """
        큐레이션 타입 2: 간단한 정보제공
        질문이 있으면 먼저 간단히 답변한 후, 작품에 대한 핵심 정보를 제공하고 더 듣기 선택지를 제시합니다.
        질문이 없으면 원래 설계대로 작품 정보와 선택지를 제시합니다.
        """
        # 질문이 있으면 먼저 간단히 답변
        question_answer = ""
        if question:
            question_answer = self._get_question_answer(art_name, question, memory)
        
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        question_section = f"관람객의 질문: {question}" if question else ""
        
        memory_section = ""
        if memory:
            memory_section = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 정보를 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt_template = self._load_prompt("prompt_2.txt")
        prompt = prompt_template.format(
            art_name=art_name,
            art_name_en=art_name_en,
            question_section=question_section,
            memory_section=memory_section
        )
        main_response = self._get_llm_response(prompt)
        
        # 질문 답변이 있으면 연결해서 반환
        if question_answer:
            return f"{question_answer} {main_response}"
        return main_response
    
    def curation_type_3(self, art_name, related_artwork, memory="", viewed_artworks=None, question=None):
        """
        큐레이션 타입 3: 간단한 비교제공 및 질문응답 deep-1으로의 유도        
        연관 작품과의 공통점과 차이점을 간단히 비교하고,
        더 자세한 설명을 들을 수 있도록 유도합니다.
        """
        # 질문이 있으면 먼저 간단히 답변
        question_answer = ""
        if question:
            question_answer = self._get_question_answer(art_name, question, memory)
        
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        related_artwork_en = ARTWORK_NAME_KR_TO_EN.get(related_artwork, related_artwork)
        
        # 비교 데이터 가져오기
        comparison_info = self._get_comparison_data(art_name, related_artwork)
        comparison_context = ""
        if comparison_info:
            comparison_context = f"\n\n참고 자료 (아래 공통점과 차이점을 참고하여 답변하세요):\n{comparison_info}"
        
        memory_section = ""
        if memory:
            memory_section = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 비교를 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt_template = self._load_prompt("prompt_3.txt")
        prompt = prompt_template.format(
            art_name=art_name,
            art_name_en=art_name_en,
            related_artwork=related_artwork,
            related_artwork_en=related_artwork_en,
            comparison_context=comparison_context,
            memory_section=memory_section
        )
        main_response = self._get_llm_response(prompt)
        
        # 질문 답변이 있으면 연결해서 반환
        if question_answer:
            return f"{question_answer} {main_response}"
        return main_response
    
    def curation_type_4(self, art_name, memory="", viewed_artworks=None, question=None):
        """
        큐레이션 타입 4: 작품과 관련된 배경지식 제공   
        작품의 시대적 배경, 사조, 철학적 배경, 작가 이야기 등
        배경지식을 정확히 3문장으로 설명합니다.
        """
        # 질문이 있으면 먼저 간단히 답변
        question_answer = ""
        if question:
            question_answer = self._get_question_answer(art_name, question, memory)
        
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        memory_section = ""
        if memory:
            memory_section = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 배경지식을 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt_template = self._load_prompt("prompt_4.txt")
        prompt = prompt_template.format(
            art_name=art_name,
            art_name_en=art_name_en,
            memory_section=memory_section
        )
        main_response = self._get_llm_response(prompt)
        
        # 질문 답변이 있으면 연결해서 반환
        if question_answer:
            return f"{question_answer} {main_response}"
        return main_response
    
    def curation_type_5(self, art_name, memory="", viewed_artworks=None, question=None):
        """
        큐레이션 타입 5: 배경지식 제공 + 관람자 느낌 묻기
        작품의 배경지식을 설명한 후, 관람자의 인상과 느낌을 묻는
        열린 질문을 던집니다.
        """
        # 질문이 있으면 먼저 간단히 답변
        question_answer = ""
        if question:
            question_answer = self._get_question_answer(art_name, question, memory)
        
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        memory_section = ""
        if memory:
            memory_section = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 배경지식을 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt_template = self._load_prompt("prompt_5.txt")
        prompt = prompt_template.format(
            art_name=art_name,
            art_name_en=art_name_en,
            memory_section=memory_section
        )
        main_response = self._get_llm_response(prompt)
        
        # 질문 답변이 있으면 연결해서 반환
        if question_answer:
            return f"{question_answer} {main_response}"
        return main_response
    
    def curation_type_6(self, art_name, related_artwork=None, memory="", viewed_artworks=None, question=None):
        """
        큐레이션 타입 6: 조형요소 + 타인의견 노출 + 관계짓기        
        다른 관람객들의 의견, 일반적 해석, 연관 작품과의 비교를 제시한 후,
        관람자가 자신의 경험이나 가치관과 작품을 연결하도록 유도하는
        열린 질문을 던집니다.
            """
        # 질문이 있으면 먼저 간단히 답변
        question_answer = ""
        if question:
            question_answer = self._get_question_answer(art_name, question, memory)
        
        # 연관 작품이 명시되지 않았다면 viewed_artworks에서 가져오기
        if not related_artwork and viewed_artworks and len(viewed_artworks) > 0:
            # 현재 작품을 제외한 마지막 관람 작품
            previous_works = [art for art in viewed_artworks if art != art_name]
            related_artwork = previous_works[-1] if previous_works else None
        
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        related_artwork_en = ARTWORK_NAME_KR_TO_EN.get(related_artwork, related_artwork) if related_artwork else None
        
        # 비교 데이터 가져오기
        comparison_context = ""
        if related_artwork:
            comparison_info = self._get_comparison_data(art_name, related_artwork)
            if comparison_info:
                comparison_context = f"\n\n참고 자료 (아래 공통점과 차이점을 참고하여 답변하세요):\n{comparison_info}"
        
        comparison_text = ""
        if related_artwork:
            comparison_text = f"연관 작품과의 공통점과 차이점을 언급하고, "
        
        related_artwork_section = f"연관 작품: {related_artwork_en} (한국어 작품명: {related_artwork})" if related_artwork else ""
        related_artwork_name_mention = f" 또는 '{related_artwork}'" if related_artwork else ""
        
        memory_section = ""
        if memory:
            memory_section = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용을 고려하여 새로운 관점을 제시하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt_template = self._load_prompt("prompt_6.txt")
        prompt = prompt_template.format(
            art_name=art_name,
            art_name_en=art_name_en,
            related_artwork_section=related_artwork_section,
            comparison_text=comparison_text,
            related_artwork_name_mention=related_artwork_name_mention,
            comparison_context=comparison_context,
            memory_section=memory_section
        )
        main_response = self._get_llm_response(prompt)
        
        # 질문 답변이 있으면 연결해서 반환
        if question_answer:
            return f"{question_answer} {main_response}"
        return main_response
    
    def route_curation(self, curation_type, art_name, memory="", viewed_artworks=None, **kwargs):
        """
        큐레이션 타입에 따라 적절한 함수로 라우팅하는 메인 함수
        
        :param curation_type: 큐레이션 타입 번호 (1-6)
        :param art_name: 작품명
        :param memory: 현재 작품에 대해 이미 생성된 정보
        :param viewed_artworks: 현재까지 관람한 작품 리스트
        :param kwargs: 타입별 추가 인자
            - question: 모든 타입에서 선택적으로 사용 가능한 사용자 질문
            - related_artwork: 타입 3, 6에서 비교할 연관 작품명
        :return: 해당 타입의 큐레이션 나레이션
        """
        question = kwargs.get('question', None)
        
        if curation_type == 1:
            return self.curation_type_1(art_name, memory, viewed_artworks, question)
        
        elif curation_type == 2:
            # Type 2는 question이 없어도 작동하도록 변경 (question이 없으면 원래 설계대로만 응답)
            return self.curation_type_2(art_name, question, memory, viewed_artworks)
        
        elif curation_type == 3:
            related_artwork = kwargs.get('related_artwork', '')
            if not related_artwork:
                return "오류: 타입 3은 'related_artwork' 파라미터가 필요합니다."
            return self.curation_type_3(art_name, related_artwork, memory, viewed_artworks, question)
        
        elif curation_type == 4:
            return self.curation_type_4(art_name, memory, viewed_artworks, question)
        
        elif curation_type == 5:
            return self.curation_type_5(art_name, memory, viewed_artworks, question)
        
        elif curation_type == 6:
            related_artwork = kwargs.get('related_artwork', None)
            return self.curation_type_6(art_name, related_artwork, memory, viewed_artworks, question)
        
        else:
            return f"오류: 잘못된 큐레이션 타입입니다. 1-6 사이의 값을 입력하세요. (입력값: {curation_type})"


# --- 사용 예시 ---
if __name__ == '__main__':
    # CurationTypes 인스턴스 생성 (환경 변수 OPENAI_API_KEY 사용)
    curation = CurationTypes()
    
    print("=== 큐레이션 타입 1: 핵심 맥락 제공 ===")
    result1 = curation.route_curation(
        curation_type=1,
        art_name="시녀들",
        memory="",
        viewed_artworks=[]
    )
    print(result1)
    print("\n" + "="*60 + "\n")
    
    print("=== 큐레이션 타입 2: 간단한 정보제공 ===")
    result2 = curation.route_curation(
        curation_type=2,
        art_name="시녀들",
        memory="",
        viewed_artworks=[],
        question="그림 가운데 있는 소녀는 누구인가요?"
    )
    print(result2)
    print("\n" + "="*60 + "\n")
    
    print("=== 큐레이션 타입 3: 비교 제공 ===")
    result3 = curation.route_curation(
        curation_type=3,
        art_name="비너스의 탄생",
        memory="",
        viewed_artworks=["프리마베라"],
        related_artwork="프리마베라"
    )
    print(result3)
    print("\n" + "="*60 + "\n")
    
    print("=== 큐레이션 타입 4: 배경지식 제공 ===")
    result4 = curation.route_curation(
        curation_type=4,
        art_name="최후의 만찬",
        memory="",
        viewed_artworks=[]
    )
    print(result4)
    print("\n" + "="*60 + "\n")
    
    print("=== 큐레이션 타입 5: 배경지식 + 느낌 묻기 ===")
    result5 = curation.route_curation(
        curation_type=5,
        art_name="야경",
        memory="",
        viewed_artworks=[]
    )
    print(result5)
    print("\n" + "="*60 + "\n")
    
    print("=== 큐레이션 타입 6: 타인의견 + 관계짓기 ===")
    result6 = curation.route_curation(
        curation_type=6,
        art_name="아테네 학당",
        memory="",
        viewed_artworks=["아담의 창조"],
        related_artwork="아담의 창조"
    )
    print(result6)
    print("\n" + "="*60 + "\n")

