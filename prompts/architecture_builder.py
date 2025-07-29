def build_architecture_prompt() -> str:
    prompt = """You are a senior systems developer. Given the previous components and system layout, write a **clear and professional architecture description** to help an AI yourself understand the design.

                Structure your architecture in **three main layers**:

                1. **UI Layer** – User interfaces, clients, and external-facing systems
                2. **Business Logic Layer** – Application logic, services, authentication, and messaging
                3. **Data Layer** – Databases, file storage, and legacy systems

                Also create a section called:

                **Component Interactions** – Describe the data flow or request flow between components (e.g. “Browser sends request → Web Server → App Server → DB”).

                Then, use the previous components and system layout to build the Application.
                """
    return prompt