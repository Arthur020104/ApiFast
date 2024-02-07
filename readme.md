Endpoints da API
1. Criar Mensagem
Método: POST
Endpoint: /create_message
Entrada:
text: Texto da mensagem (string)
is_user: Indica se a mensagem é do usuário (boolean)
datetime: Data e hora da mensagem (formato datetime)
conversation_id: ID da conversa à qual a mensagem pertence (integer)
Saída:
message_id: ID da mensagem criada (integer)
status: Status da operação (dict)
2. Obter Mensagem por ID
Método: GET
Endpoint: /get_message/{message_id}
Entrada:
message_id: ID da mensagem a ser recuperada (integer)
Saída:
message_id: ID da mensagem recuperada (integer)
message_content: Conteúdo da mensagem (string)
status: Status da operação (dict)
3. Adicionar Mensagem à Conversa
Método: POST
Endpoint: /add_message_to_conversation/{conversation_id}
Entrada:
conversation_id: ID da conversa à qual a mensagem será adicionada (integer)
text: Texto da mensagem (string)
is_user: Indica se a mensagem é do usuário (boolean)
datetime: Data e hora da mensagem (formato datetime)
Saída:
message_id: ID da mensagem adicionada (integer)
status: Status da operação (dict)
4. Atualizar Mensagem por ID
Método: PUT
Endpoint: /update_message/{message_id}
Entrada:
message_id: ID da mensagem a ser atualizada (integer)
text: Novo texto da mensagem (opcional)
is_user: Indica se a mensagem é do usuário (opcional)
datetime: Nova data e hora da mensagem (opcional)
Saída:
message_id: ID da mensagem atualizada (integer)
updated_message: Mensagem atualizada (conteúdo, ID, etc.)
status: Status da operação (dict)
5. Excluir Mensagem por ID
Método: DELETE
Endpoint: /delete_message/{message_id}
Entrada:
message_id: ID da mensagem a ser excluída (integer)
Saída:
message_id: ID da mensagem excluída (integer)
status: Status da operação (dict)
6. Criar Conversa
Método: POST
Endpoint: /create_conversation
Entrada:
user_id: ID do usuário associado à conversa (integer)
Saída:
conversation_id: ID da conversa criada (integer)
messages: Lista vazia de mensagens associadas à conversa
status: Status da operação (dict)