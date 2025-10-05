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
    
    def __init__(self, api_key=None, comparison_data_path="assets/llm/transformed_pair.json"):
        """
        CurationTypes 클래스를 초기화합니다.
        
        :param api_key: OpenAI API 키. None이면 환경 변수에서 찾습니다.
        :param comparison_data_path: 작품 비교 데이터 JSON 파일 경로
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "OpenAI API 키가 설정되지 않았습니다. "
                "환경 변수 OPENAI_API_KEY를 설정하거나 api_key 파라미터를 전달하세요."
            )
        
        self.client = OpenAI(api_key=api_key)
        
        # 작품 비교 데이터 로드
        self.comparison_data = {}
        try:
            with open(comparison_data_path, 'r', encoding='utf-8') as f:
                self.comparison_data = json.load(f)
        except FileNotFoundError:
            print(f"경고: 비교 데이터 파일을 찾을 수 없습니다: {comparison_data_path}")
        except json.JSONDecodeError:
            print(f"경고: 비교 데이터 파일을 읽을 수 없습니다: {comparison_data_path}")
    
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
    
    def curation_type_1(self, art_name, memory="", viewed_artworks=None):
        """
        큐레이션 타입 1: 작품 설명의 핵심 맥락 제공
        작품의 핵심 주제와 맥락을 120~170자로 간결하게 설명합니다.
        """
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        context_info = ""
        if memory:
            context_info = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 관점을 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt = f"""당신은 미술관 큐레이터입니다. 
작품 '{art_name_en}'의 핵심 주제와 맥락을 간결하게 설명해주세요.
조형적 특징(구도, 색채 등)과 작품의 의미를 함께 언급하세요.

**글자 수 제약: 120자 이상 170자 이하**
- 반드시 120자 이상 170자 이하로 작성하세요

**중복 방지: 이미 설명한 내용은 되도록 반복하지 마세요**
- 설명을 위해 어쩔 수 없이 필요한 경우에만 "앞서 언급했듯"이라고 말하며 간단히 언급하세요

**중요: TTS(음성 합성)를 위한 출력 형식**
- 자연스러운 구어체로 작성하세요
- 따옴표, 괄호, 특수기호 등은 사용하지 마세요
- 음성으로 읽었을 때 자연스럽게 들리도록 작성하세요
- 모든 문장의 종결어미는 반드시 "~니다" 체를 사용하세요 (예: ~합니다, ~입니다, ~습니다)
- 작품명을 언급할 때는 반드시 한국어 작품명 '{art_name}'을(를) 사용하세요

예시: "전후 상실을 개인 초상으로 응축한 작품입니다. 사선 구도와 냉색 대비가 고립감을 강화합니다."
{context_info}
"""
        return self._get_llm_response(prompt)
    
    def curation_type_2(self, art_name, question, memory="", viewed_artworks=None):
        """
        큐레이션 타입 2: 간단한 정보제공
        사용자의 질문에 대해 핵심 정보를 1문장으로 답하고,
        더 듣기 선택지를 제시합니다.
        """
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        context_info = ""
        if memory:
            context_info = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 정보를 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt = f"""당신은 미술관 큐레이터입니다.

작품명: {art_name_en} (한국어 작품명: {art_name})
관람객의 질문: {question}

1. 먼저 질문의 핵심을 1문장으로 확인하세요.
2. 그 다음 작품에 대한 핵심 정보를 1문장으로 답변하세요.
3. 마지막으로 더 듣기 선택지를 1문장으로 제시하세요.

**분량 제약: 최대 3문장 (1–2문장 답변 + 선택지 1문장)**
**전문용어 최소화: 일반인도 이해할 수 있는 쉬운 표현 사용**
**단정/가치판단 금지: 객관적 사실 중심으로 서술**

**중복 방지: 이미 설명한 내용은 되도록 반복하지 마세요**
- 설명을 위해 어쩔 수 없이 필요한 경우에만 "앞서 언급했듯"이라고 말하며 간단히 언급하세요

**중요: TTS(음성 합성)를 위한 출력 형식**
- 자연스러운 구어체로 작성하세요
- 따옴표, 괄호, 특수기호 등은 사용하지 마세요
- 음성으로 읽었을 때 자연스럽게 들리도록 작성하세요
- 모든 문장의 종결어미는 반드시 "~니다" 체를 사용하세요 (예: ~합니다, ~입니다, ~습니다)
- 작품명을 언급할 때는 반드시 한국어 작품명 '{art_name}'을(를) 사용하고 따옴표 없이 자연스럽게 말하세요

예시: "작가의 스승입니다. 그의 화풍이 여기에도 드러납니다. 배경을 더 들어보시겠습니까, 아니면 비슷한 작품을 보시겠습니까?"
{context_info}
"""
        return self._get_llm_response(prompt)
    
    def curation_type_3(self, art_name, related_artwork, memory="", viewed_artworks=None):
        """
        큐레이션 타입 3: 간단한 비교제공 및 질문응답 deep-1으로의 유도        
        연관 작품과의 공통점과 차이점을 간단히 비교하고,
        더 자세한 설명을 들을 수 있도록 유도합니다.
        """
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        related_artwork_en = ARTWORK_NAME_KR_TO_EN.get(related_artwork, related_artwork)
        
        context_info = ""
        if memory:
            context_info = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 비교를 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        # 비교 데이터 가져오기
        comparison_info = self._get_comparison_data(art_name, related_artwork)
        comparison_context = ""
        if comparison_info:
            comparison_context = f"\n\n참고 자료 (아래 공통점과 차이점을 참고하여 답변하세요):\n{comparison_info}"
        
        prompt = f"""당신은 미술관 큐레이터입니다.

작품명: {art_name_en} (한국어 작품명: {art_name})
연관 작품: {related_artwork_en} (한국어 작품명: {related_artwork})

1. 두 작품의 공통점 1개를 1구로 언급하세요.
2. 두 작품의 차이점 1개를 1구로 언급하세요.
3. 더 자세한 설명을 듣도록 유도하는 선택지를 1문장으로 제시하세요.

**구성: 한 문장 비교(공통점→차이점 순서) + 선택지 1문장**
**수치/전문용어 과다 금지: 일반적이고 쉬운 표현 사용**

**중복 방지: 이미 설명한 내용은 되도록 반복하지 마세요**
- 설명을 위해 어쩔 수 없이 필요한 경우에만 "앞서 언급했듯"이라고 말하며 간단히 언급하세요

**중요: TTS(음성 합성)를 위한 출력 형식**
- 자연스러운 구어체로 작성하세요
- 따옴표, 괄호, 특수기호 등은 사용하지 마세요
- 음성으로 읽었을 때 자연스럽게 들리도록 작성하세요
- 모든 문장의 종결어미는 반드시 "~니다" 체를 사용하세요 (예: ~합니다, ~입니다, ~습니다)
- 작품명을 언급할 때는 반드시 한국어 작품명 '{art_name}'과(와) '{related_artwork}'을(를) 사용하고 따옴표 없이 자연스럽게 말하세요

예시: "이 작품과 프리마베라는 같은 주제를 다루지만, 여기는 색을 단순화하고 프리마베라는 세부 묘사가 풍부합니다. 자세히 알아보시겠습니까?"
{comparison_context}
{context_info}
"""
        return self._get_llm_response(prompt)
    
    def curation_type_4(self, art_name, memory="", viewed_artworks=None):
        """
        큐레이션 타입 4: 작품과 관련된 배경지식 제공   
        작품의 시대적 배경, 사조, 철학적 배경, 작가 이야기 등
        배경지식을 정확히 3문장으로 설명합니다.
        """
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        context_info = ""
        if memory:
            context_info = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 배경지식을 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt = f"""당신은 미술관 큐레이터입니다.

작품명: {art_name_en} (한국어 작품명: {art_name})

작품의 배경지식을 설명해주세요. 다음 요소를 포함하세요:
- 제작 시기
- 예술 사조
- 작가 정보
- 시대적/철학적 컨텍스트

**분량 제약: 정확히 3문장**
- 반드시 3문장으로 작성하세요

**중복 방지: 이미 설명한 내용은 되도록 반복하지 마세요**
- 설명을 위해 어쩔 수 없이 필요한 경우에만 "앞서 언급했듯"이라고 말하며 간단히 언급하세요

**중요: TTS(음성 합성)를 위한 출력 형식**
- 자연스러운 구어체로 작성하세요
- 따옴표, 괄호, 특수기호 등은 사용하지 마세요
- 음성으로 읽었을 때 자연스럽게 들리도록 작성하세요
- 모든 문장의 종결어미는 반드시 "~니다" 체를 사용하세요 (예: ~합니다, ~입니다, ~습니다)
- 작품명을 언급할 때는 반드시 한국어 작품명 '{art_name}'을(를) 사용하고 따옴표 없이 자연스럽게 말하세요

예시: "이 작품은 19세기 말 파리에서 활동한 인상주의 작가가 제작한 도시 풍경 시리즈 중 하나로, 당시 도시의 변화와 사람들의 일상을 담고 있습니다."
{context_info}
"""
        return self._get_llm_response(prompt)
    
    def curation_type_5(self, art_name, memory="", viewed_artworks=None):
        """
        큐레이션 타입 5: 배경지식 제공 + 관람자 느낌 묻기
        작품의 배경지식을 설명한 후, 관람자의 인상과 느낌을 묻는
        열린 질문을 던집니다.
        """
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        context_info = ""
        if memory:
            context_info = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용과 중복되지 않는 새로운 배경지식을 제공하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        prompt = f"""당신은 미술관 큐레이터입니다.

작품명: {art_name_en} (한국어 작품명: {art_name})

1. 작품의 배경지식을 3문장 이내로 설명하세요 (제작시기, 사조, 작가, 컨텍스트 포함)
2. 이어서 관람자의 느낌이나 선호를 묻는 열린 질문을 1문장 생성하세요

**분량 제약: 정확히 4문장 (배경지식 3문장 + 질문 1문장)**
**톤: 친근하고 중립적인 톤 유지**
**질문 포함: 반드시 관람자에게 묻는 질문 포함**

**중복 방지: 이미 설명한 내용은 되도록 반복하지 마세요**
- 설명을 위해 어쩔 수 없이 필요한 경우에만 "앞서 언급했듯"이라고 말하며 간단히 언급하세요

**중요: TTS(음성 합성)를 위한 출력 형식**
- 자연스러운 구어체로 작성하세요
- 따옴표, 괄호, 특수기호 등은 사용하지 마세요
- 음성으로 읽었을 때 자연스럽게 들리도록 작성하세요
- 모든 문장의 종결어미는 반드시 "~니다" 체를 사용하세요 (예: ~합니다, ~입니다, ~습니다)
- 작품명을 언급할 때는 반드시 한국어 작품명 '{art_name}'을(를) 사용하고 따옴표 없이 자연스럽게 말하세요
- 질문은 자연스럽게 대화하듯 던지세요

예시: "이 작품은 19세기 말 파리에서 활동한 인상주의 작가가 제작한 도시 풍경 시리즈 중 하나로, 당시 도시의 변화와 사람들의 일상을 담고 있습니다. 이 색감과 구도가 당신에게는 어떤 느낌을 줍니까? 특별히 마음에 드는 부분이 있으십니까?"
{context_info}
"""
        return self._get_llm_response(prompt)
    
    def curation_type_6(self, art_name, related_artwork=None, memory="", viewed_artworks=None):
        """
        큐레이션 타입 6: 조형요소 + 타인의견 노출 + 관계짓기        
        다른 관람객들의 의견, 일반적 해석, 연관 작품과의 비교를 제시한 후,
        관람자가 자신의 경험이나 가치관과 작품을 연결하도록 유도하는
        열린 질문을 던집니다.
            """
        # 연관 작품이 명시되지 않았다면 viewed_artworks에서 가져오기
        if not related_artwork and viewed_artworks and len(viewed_artworks) > 0:
            # 현재 작품을 제외한 마지막 관람 작품
            previous_works = [art for art in viewed_artworks if art != art_name]
            related_artwork = previous_works[-1] if previous_works else None
        
        # 영어 작품명으로 변환
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        related_artwork_en = ARTWORK_NAME_KR_TO_EN.get(related_artwork, related_artwork) if related_artwork else None
        
        context_info = ""
        if memory:
            context_info = f"\n\n이미 설명한 내용:\n{memory}\n\n위 내용을 고려하여 새로운 관점을 제시하세요. 이미 설명한 내용을 다시 언급해야 한다면 '앞서 언급했듯'이라고 말하세요."
        
        # 비교 데이터 가져오기
        comparison_context = ""
        if related_artwork:
            comparison_info = self._get_comparison_data(art_name, related_artwork)
            if comparison_info:
                comparison_context = f"\n\n참고 자료 (아래 공통점과 차이점을 참고하여 답변하세요):\n{comparison_info}"
        
        comparison_text = ""
        if related_artwork:
            comparison_text = f"연관 작품과의 공통점과 차이점을 언급하고, "
        
        prompt = f"""당신은 미술관 큐레이터입니다.

작품명: {art_name_en} (한국어 작품명: {art_name})
{f"연관 작품: {related_artwork_en} (한국어 작품명: {related_artwork})" if related_artwork else ""}

다음 내용을 구성하세요:
1. 다른 관람객들이 자주 느끼는 점이나 일반적인 해석을 1문장으로 언급
2. {comparison_text if related_artwork else ""}조형적 특징(색감, 구도 등)을 언급
3. 관람자가 자신의 경험이나 가치관과 작품을 연결하도록 유도하는 열린 질문 1문장

**분량 제약: 정확히 4문장**
**공통점·차이점 포함: 연관 작품이 있을 경우 반드시 비교**
**열린 질문 포함: 관람자의 생각과 연결하는 질문 필수**
**톤: 긍정적이고 중립적인 톤 유지**

**중복 방지: 이미 설명한 내용은 되도록 반복하지 마세요**
- 설명을 위해 어쩔 수 없이 필요한 경우에만 "앞서 언급했듯"이라고 말하며 간단히 언급하세요

**중요: TTS(음성 합성)를 위한 출력 형식**
- 자연스러운 구어체로 작성하세요
- 따옴표, 괄호, 특수기호 등은 사용하지 마세요
- 음성으로 읽었을 때 자연스럽게 들리도록 작성하세요
- 모든 문장의 종결어미는 반드시 "~니다" 체를 사용하세요 (예: ~합니다, ~입니다, ~습니다)
- 작품명을 언급할 때는 반드시 한국어 작품명 '{art_name}'{f" 또는 '{related_artwork}'" if related_artwork else ""}을(를) 사용하고 따옴표 없이 자연스럽게 말하세요
- 대화하듯 자연스럽고 친근하게 작성하세요

예시: "많은 분들이 이 작품의 강렬한 색감과 구도가 당시 사회의 긴장과 희망을 함께 전한다고 느끼며, 아까 보신 작품과 비교하면 표현 방식은 다르지만 주제의식은 유사하다고 이야기합니다. 당신은 이런 표현이 본인의 경험이나 가치관과도 닮았다고 느끼십니까?"
{comparison_context}
{context_info}
"""
        return self._get_llm_response(prompt)
    
    def route_curation(self, curation_type, art_name, memory="", viewed_artworks=None, **kwargs):
        """
        큐레이션 타입에 따라 적절한 함수로 라우팅하는 메인 함수
        
        :param curation_type: 큐레이션 타입 번호 (1-6)
        :param art_name: 작품명
        :param memory: 현재 작품에 대해 이미 생성된 정보
        :param viewed_artworks: 현재까지 관람한 작품 리스트
        :param kwargs: 타입별 추가 인자
            - question: 타입 2에서 사용자 질문
            - related_artwork: 타입 3, 6에서 비교할 연관 작품명
        :return: 해당 타입의 큐레이션 나레이션
        """
        if curation_type == 1:
            return self.curation_type_1(art_name, memory, viewed_artworks)
        
        elif curation_type == 2:
            question = kwargs.get('question', '')
            if not question:
                return "오류: 타입 2는 'question' 파라미터가 필요합니다."
            return self.curation_type_2(art_name, question, memory, viewed_artworks)
        
        elif curation_type == 3:
            related_artwork = kwargs.get('related_artwork', '')
            if not related_artwork:
                return "오류: 타입 3은 'related_artwork' 파라미터가 필요합니다."
            return self.curation_type_3(art_name, related_artwork, memory, viewed_artworks)
        
        elif curation_type == 4:
            return self.curation_type_4(art_name, memory, viewed_artworks)
        
        elif curation_type == 5:
            return self.curation_type_5(art_name, memory, viewed_artworks)
        
        elif curation_type == 6:
            related_artwork = kwargs.get('related_artwork', None)
            return self.curation_type_6(art_name, related_artwork, memory, viewed_artworks)
        
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

