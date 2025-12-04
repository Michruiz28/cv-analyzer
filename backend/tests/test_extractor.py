from agents.extractor_agent import ExtractorAgent

agent = ExtractorAgent()

pdf_path = "C:\\Users\\michr\\Downloads\\HOJADEVIDA.pdf"

result = agent.process_cv(pdf_path)

print(result)
