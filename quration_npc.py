import json
import os
import random
from openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader

class CuratorNPC:
    """
    미술관 큐레이터 NPC의 역할을 수행하는 클래스.
    다양한 시나리오에 맞는 발화문을 생성합니다.
    """
    def __init__(self, section_data_path, common_and_different_path, prompts_dir, documents_dir, api_key=None):
        """
        CuratorNPC 클래스를 초기화합니다.

        :param section_data_path: 섹션 및 작품 정보가 담긴 JSON 파일 경로
        :param common_and_different_path: 공통 및 차별화 정보가 담긴 JSON 파일 경로
        :param prompts_dir: 프롬프트 템플릿 파일이 있는 디렉터리 경로
        :param documents_dir: RAG에 사용할 문서 파일이 있는 디렉터리 경로
        :param api_key: OpenAI API 키. None이면 환경 변수에서 찾습니다.
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=api_key)
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=api_key)
        
        with open(section_data_path, "r", encoding="utf-8") as f:
            self.section_data = json.load(f)
        with open(common_and_different_path, "r", encoding="utf-8") as f:
            self.common_and_different_data = json.load(f)
            
        self.section_1_description = self.section_data[0]["description"]
        self.section_2_description = self.section_data[1]["description"]

        # 프롬프트 템플릿 로드
        self.prompts = {}
        for filename in os.listdir(prompts_dir):
            if filename.endswith(".txt"):
                prompt_name = filename.split('.')[0]
                with open(os.path.join(prompts_dir, filename), "r", encoding="utf-8") as f:
                    self.prompts[prompt_name] = f.read()
        # RAG 시스템 설정
        self.rag_chains = self._setup_rag(documents_dir)

    def _setup_rag(self, documents_dir):
        """지정된 디렉터리의 작품별 문서에 대해 각각 RAG 시스템을 설정합니다."""
        rag_chains = {}
        try:
            for filename in os.listdir(documents_dir):
                if filename.endswith(".txt"):
                    art_name = filename.split('.')[0]
                    document_path = os.path.join(documents_dir, filename)
                    
                    loader = TextLoader(document_path, encoding='utf-8')
                    documents = loader.load()
                    
                    if not documents:
                        print(f"'{art_name}'에 대한 문서를 찾을 수 없습니다. 건너뜁니다.")
                        continue

                    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                    docs = text_splitter.split_documents(documents)
                    
                    embedding = OpenAIEmbeddings()
                    db = FAISS.from_documents(docs, embedding)
                    
                    retriever = db.as_retriever()
                    qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=retriever)
                    rag_chains[art_name] = qa_chain
                    print(f"'{art_name}' 작품에 대한 RAG 시스템을 성공적으로 설정했습니다.")
            
            return rag_chains
        except Exception as e:
            print(f"RAG 설정 중 오류 발생: {e}")
            return {}

    def _get_llm_response(self, prompt, temperature=0.7):
        """OpenAI API를 호출하여 응답을 반환하는 내부 메서드"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content

    def _get_initial_section_narration(self, current_section):
        """처음 입장한 관람객에게 현재 섹션과 다른 섹션을 안내합니다."""
        prompt_template = self.prompts.get('section_narration_initial', '')
        prompt = prompt_template.format(
            section_1_description=self.section_1_description,
            section_2_description=self.section_2_description,
            current_section=current_section
        )

        return self._get_llm_response(prompt)

    def _get_transition_section_narration(self, current_section, previous_work):
        """이전 감상 작품과 연결하여 다음 섹션을 안내합니다."""
        prompt_template = self.prompts.get('section_narration_with_history', '')
        prompt = prompt_template.format(
            section_1_description=self.section_1_description,
            section_2_description=self.section_2_description,
            current_section=current_section,
            previous_work=previous_work
        )
        return self._get_llm_response(prompt)

    def get_section_narration(self, current_section, previous_work=None):
        """
        현재 섹션에 대한 안내 메시지를 생성합니다.
        이전 작품이 주어지면 섹션 전환 안내도 포함됩니다.
        
        :param current_section: 현재 섹션 번호 (1 또는 2)
        :param previous_work: 이전에 감상한 작품 이름 (선택적)
        :return: 안내 메시지 문자열
        """
        if previous_work:
            return self._get_transition_section_narration(current_section, previous_work)
        else:
            return self._get_initial_section_narration(current_section)


    def get_artwork_attraction_narration(self, current_section, viewed_artworks):
        """
        현재 섹션의 작품 중 아직 관람하지 않은 작품 하나를 랜덤으로 골라 흥미를 유발하는 질문을 생성합니다.
        
        :param current_section: 현재 섹션 번호 (1 또는 2)
        :param viewed_artworks: 이미 관람한 작품 이름 리스트
        :return: 흥미 유발 메시지 문자열 또는 관람할 작품이 없을 경우 안내 메시지
        """
        # 현재 섹션의 모든 작품 목록 가져오기
        section_info = next((s for s in self.section_data if s['level'] == current_section), None)
        if not section_info:
            return "잘못된 섹션 번호입니다."

        all_artworks_in_section = section_info.get("arts", [])
        
        # 아직 관람하지 않은 작품 목록 필터링
        unviewed_artworks = [art for art in all_artworks_in_section if art not in viewed_artworks]

        if not unviewed_artworks:
            return "이 섹션의 모든 작품을 감상하셨네요! 다른 섹션도 둘러보시는 건 어떠세요?"

        # 관람하지 않은 작품 중 하나를 랜덤으로 선택
        art_name = random.choice(unviewed_artworks)

        prompt_template = self.prompts.get('artwork_attraction_narration', '')
        prompt = prompt_template.format(art_name=art_name)
        return self._get_llm_response(prompt)

    def _get_artwork_narration_initial(self, art_name, memory=""):
        """작품에 대한 핵심 정보를 설명합니다. 이미 설명한 내용은 제외합니다."""
        prompt_template = self.prompts.get('artwork_narration_initial', '')
        prompt = prompt_template.format(art_name=art_name, memory=memory)
        return self._get_llm_response(prompt)
    

    def _get_artwork_narration_additional(self, art_name, memory=""):
        """작품에 대한 핵심 정보를 설명합니다. 이미 설명한 내용은 제외합니다."""
        prompt_template = self.prompts.get('artwork_narration_additional', '')
        prompt = prompt_template.format(art_name=art_name, memory=memory)
        return self._get_llm_response(prompt)
    

    def _get_artwork_narration_with_history(self, art_name, previous_work):
        key1=f"{art_name}-{previous_work}"
        key2=f"{previous_work}-{art_name}"
        """작품에 대한 핵심 정보를 설명합니다. 이미 설명한 내용은 제외합니다."""
        prompt_template = self.prompts.get('artwork_narration_with_history', '')
        if key1 in self.common_and_different_data:
            common_and_different = key1
        elif key2 in self.common_and_different_data:
            common_and_different = key2
        prompt = prompt_template.format(art_name=art_name, previous_work=previous_work, common_and_different=common_and_different)
        return self._get_llm_response(prompt)
    

    


    def get_artwork_narration(self, art_name, memory="", viewed_artworks=None):
        """
        작품에 대한 설명을 생성합니다.
        이전 작품이 주어지면 공통점과 차이점을 포함합니다.
        
        :param art_name: 작품 이름
        :param previous_work: 이전에 감상한 작품 이름 (선택적)
        :param memory: 이미 설명한 내용 (선택적)
        :return: 작품 설명 문자열
        """
        if viewed_artworks:
            if memory=="":
                return self._get_artwork_narration_with_history(art_name, viewed_artworks[-1])
            else:
                return self._get_artwork_narration_additional(art_name, memory)
        
        else:
            if memory=="":
                return self._get_artwork_narration_initial(art_name, memory)
            else:
                return self._get_artwork_narration_additional(art_name, memory)
                

    def answer_question_with_rag(self, question, art_name):
        """지정된 작품의 RAG 시스템을 사용하여 질문에 답변합니다."""
        if not self.rag_chains:
            return "RAG 시스템이 설정되지 않았습니다."
        
        qa_chain = self.rag_chains.get(art_name)
        if not qa_chain:
            return f"'{art_name}' 작품에 대한 정보가 없습니다."
        
        answer = qa_chain.run(question)
        return answer

# --- 클래스 사용 예시 ---
if __name__ == '__main__':
    # API 키 로드 (실제 사용 시에는 환경 변수 설정을 권장합니다)
    # from dotenv import load_dotenv
    # load_dotenv()

    # 1. CuratorNPC 인스턴스 생성
    # 파일 경로는 실제 환경에 맞게 수정해주세요.
    section_data_file = '/Users/sngwon/python/xr/contents/assets/section_level_data.json'
    prompts_directory = '/Users/sngwon/python/xr/contents/prompts'
    documents_directory = '/Users/sngwon/python/xr/contents/assets/document'
    common_and_different_path= '/Users/sngwon/python/xr/contents/assets/transformed_pair.json'
    curator = CuratorNPC(
        section_data_path=section_data_file, 
        common_and_different_path=common_and_different_path,
        prompts_dir=prompts_directory,
        documents_dir=documents_directory
    )

    # # 2. 시나리오별 메서드 호출
    # print("--- 초기 섹션 안내 ---")
    # narration1 = curator.get_section_narration(current_section=1)
    # print(narration1)
    # print("\n" + "="*50 + "\n")

    # print("--- 작품 감상 후 섹션 이동 안내 ---")
    # narration2 = curator.get_section_narration(current_section=1, previous_work="프리마베라")
    # print(narration2)
    # print("\n" + "="*50 + "\n")

    # print("--- 작품 흥미 유발 ---")
    # # 예시: 1번 섹션에서 '프리마베라'를 이미 관람했다고 가정
    # viewed_artworks = ["프리마베라"]
    # narration3 = curator.get_artwork_attraction_narration(current_section=1, viewed_artworks=viewed_artworks)
    # print(narration3)
    # print("\n" + "="*50 + "\n")



    # print("--- 작품 설명 / 첫 관람 작품, 첫 번째 발화---")
    # memory=""
    # viewed_artworks = []
    # art_name="비너스의 탄생"
    # narration4 = curator.get_artwork_narration(art_name=art_name, memory=memory, viewed_artworks=viewed_artworks)
    # print(narration4)
    # print("\n" + "="*50 + "\n")

    # print("--- 작품 설명 / 첫 관람 작품, 두 번째 이상 발화 ---")
    # memory="비너스의 탄생은 이탈리아의 화가 산드로 보티첼리의 대표작으로 1484년에서 1486년 사이에 제작되었습니다. 이 작품은 고대 그리스 신화에 등장하는 사랑과 미의 여신 비너스의 탄생 순간을 그린 것으로 유명합니다. 그림의 중앙에는 비너스가 조개껍질 위에 서 있는 모습이 그려져 있으며 그녀의 아름다움은 보는 이의 시선을 사로잡습니다. 비너스의 주위에는 다양한 신화적 인물들이 등장하는데, 왼쪽에는 바람의 신 제피루스와 그의 아내 클로리스가 비너스를 부드럽게 감싸고 있으며 오른쪽에는 비너스의 환복을 도와주는 여신들이 있습니다. 작품은 섬세한 색채와 유려한 선이 특징이며, 인체의 아름다움과 자연의 조화로운 모습을 잘 표현하고 있습니다. 비너스의 탄생은 인류의 이상적인 아름다움에 대한 탐구와 르네상스 시대의 인문주의적 가치관을 잘 드러내는 작품입니다. 이 그림은 오늘날에도 많은 사람들에게 사랑받고 있으며, 미술사에서 중요한 위치를 차지하고 있습니다."
    # viewed_artworks = []
    # art_name="비너스의 탄생"
    # narration4 = curator.get_artwork_narration(art_name=art_name, memory=memory, viewed_artworks=viewed_artworks)
    # print(narration4)
    # print("\n" + "="*50 + "\n")

    # print("--- 작품 설명 / 두번째 이상 관람 작품, 첫 번째 발화---")
    # memory=""
    # viewed_artworks = ["프리마베라"]
    # art_name="비너스의 탄생"
    # narration4 = curator.get_artwork_narration(art_name=art_name, memory=memory, viewed_artworks=viewed_artworks)
    # print(narration4)
    # print("\n" + "="*50 + "\n")




    print("--- RAG를 이용한 질의응답 ---")
    if curator.rag_chains:
        question = "그림에서 가운데 있는 소녀는 누구야?"
        art_name_for_question = "시녀들" # 질문 대상 작품 지정
        answer = curator.answer_question_with_rag(question, art_name_for_question)
        print(f"작품: {art_name_for_question}")
        print(f"질문: {question}")
        print(f"답변: {answer}")