"""Narrador — a camada de LINGUAGEM do sistema.

Princípio de desenho, e a razão de ser defensável: **o LLM escreve a língua, nunca os factos.**
Todos os números vêm dos motores determinísticos (deteção de anomalia, decomposição,
retrieval de precedentes, triagem); o modelo só os põe numa frase legível, e é proibido de
introduzir qualquer valor que não esteja no input que recebeu.

Por agora só está construída a canalização (`providers`). A função de narração e o arnês de
fidelidade — a parte que constitui a contribuição — entram a seguir.
"""

from investigator.narrator.providers import LLMResponse, available, complete

__all__ = ["LLMResponse", "available", "complete"]
