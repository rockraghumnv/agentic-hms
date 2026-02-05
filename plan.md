project title: Personlised AI healthcare assisstent chatbot

tech stack: HTML, CSS, JS(frontend); fastapi Gemini llm api(gemini-2.5-flash), MCP client and server, Agent Development Kit , any simple vector DB , any OCR tool venv 

note: every commonds should be exucuted in venv itself

description: an healthcare chatbot build for hospitals to give personlised answers to patients based on thier past medical history stored in hospital DB ; patient asks mild fever with cough agent pulls his medical history and answers. 

features to include :
    expalin AI medical document explainer in multi-lang (kannada and simple english) user uploads med reports such as lab reports and prescription in image format only AI bot explains it in the easy and simple language any non med guy can understand; explanation
    should be personised to patient past helath records stored in db;
    for this give a button 'see explaination' where i can see how you came up with this response kind of explanable AI 

    autonomous appointment booking: if AI feels the user query or condition is severe it asks to book appointment with this doctor basically it provides a button for appointment booking and confirms the booking time plus provides instant first aid



Unique Autonomous Feature - Smart Health Timeline & Predictive Wellness Alerts:
- AI auto-generates visual health timeline from uploaded documents and detects patterns (e.g., blood sugar rising from 95→110→128 over 6 months)
- Proactively suggests screenings based on time elapsed and risk factors without user asking (e.g., "18 months since eye checkup, diabetes risk detected")
- Autonomously extracts medication schedules from prescriptions and sets up reminders with refill alerts
- Connects dots across documents that humans would miss (links family history to current test results, medication side effects to symptoms)

now we are building demo project where we give a portal for user to upload his medical docs or past medical records in image format only then generate an unique id for that uploaded user user should store the id somewhere and then he can come to chat bot and ask questions reagarding his health and AI responses and takes appropriate action 


give a small content where user can tick the button while uplaoding the med docs 

