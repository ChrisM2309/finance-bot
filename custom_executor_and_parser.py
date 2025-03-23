from langchain.agents import AgentExecutor
from langchain_core.agents import AgentAction, AgentFinish
from langchain.agents.conversational_chat.output_parser import ConvoOutputParser

class CustomOutputParser(ConvoOutputParser):
    """Parser personalizado para devolver la observación completa."""
    def parse(self, text: str):
        print("DEBUG - Parser Input:", text)
        if "Observation:" in text:
            observation = text.split("Observation:")[1].strip()
            print("DEBUG - Parsed Observation:", observation)
            return {"output": observation}
        else:
            parsed = super().parse(text)
            print("DEBUG - Default Parsed Output:", parsed)
            return parsed

class CustomAgentExecutor(AgentExecutor):
    def _call(self, inputs, run_manager=None):
        """Ejecuta el agente y devuelve la última observación completa de la herramienta en el formato correcto."""
        intermediate_steps = []
        
        if run_manager:
            callbacks = run_manager.get_child()
        else:
            callbacks = None

        while True:
            agent_scratchpad = self._construct_scratchpad(intermediate_steps)
            agent_input = {**inputs, "agent_scratchpad": agent_scratchpad}
            
            output = self.agent.plan(
                intermediate_steps=intermediate_steps,
                callbacks=callbacks,
                **agent_input
            )
            
            if isinstance(output, AgentAction):
                tool = next(t for t in self.tools if t.name == output.tool)
                observation = tool.func(output.tool_input)
                intermediate_steps.append((output, observation))
                print("DEBUG - Action:", output)
                print("DEBUG - Observation:", observation)
            
            elif isinstance(output, AgentFinish):
                print("DEBUG - Agent Finished with:", output.return_values)
                for action, observation in reversed(intermediate_steps):
                    if observation:
                        print("DEBUG - Returning Observation:", observation)
                        return {"output": observation}  # Devolver como diccionario
                print("DEBUG - Returning Default Output:", output.return_values["output"])
                return {"output": output.return_values["output"]}  # Devolver como diccionario
            
            else:
                raise ValueError(f"Unexpected output type: {type(output)}")

    def _construct_scratchpad(self, intermediate_steps):
        """Construye el scratchpad para el agente conversacional."""
        from langchain_core.messages import AIMessage
        scratchpad = []
        for action, observation in intermediate_steps:
            scratchpad.append(AIMessage(content=f"Action: {action.tool}\nInput: {action.tool_input}\nObservation: {observation}"))
        return scratchpad