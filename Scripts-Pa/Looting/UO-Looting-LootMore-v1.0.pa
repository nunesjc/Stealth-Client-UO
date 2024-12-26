program UOSlaveOwnerLoot;

procedure loot;
var
  corpse, item: Cardinal;
  itemIds: array[0..28] of integer;
  i: Integer;
begin
  itemIds[0] := $26B7;
  itemIds[1] := $0EED;
  itemIds[2] := $0FBF;
  itemIds[3] := $0FC0;
  itemIds[4] := $0FC1;
  itemIds[5] := $0FC3;
  itemIds[6] := $0FC4;
  itemIds[7] := $0FC5;
  itemIds[8] := $0FC6;
  itemIds[9] := $0F09;
  itemIds[10] := $0F0E;
  itemIds[11] := $175D;
  itemIds[12] := $0F0C;
  itemIds[13] := $0F09;
  itemIds[14] := $3155;
  itemIds[15] := $0E75; // novo
  itemIds[16] := $1BFB;
  itemIds[17] := $0F3F;
  itemIds[18] := $1412;
  itemIds[19] := $1415;
  itemIds[20] := $13B9;
  itemIds[21] := $1414;
  itemIds[22] := $1413;
  itemIds[23] := $1411;
  itemIds[24] := $1410;
  itemIds[25] := $1B76;
  itemIds[26] := $1B76;
  itemIds[27] := $1B76;
  itemIds[28] := $1F31;

  FindDistance := 3;
  if FindType($2006, Ground) > 0 then // Procura por corpos no chão (ID $2006)
  begin
    corpse := FindItem; // Pega o ID do corpo encontrado
    UseObject(corpse); // Interage com o corpo para acessar o inventário
    Wait(200); // Aguarda um pouco para o inventário abrir (ajuste conforme necessário)

    // Varre a lista de IDs de itens para saquear
    for i := 0 to High(itemIds) do
    begin
      // Se um dos itens desejados está no corpo, saqueia o item
      if FindType(itemIds[i], corpse) > 0 then
      begin
        item := FindItem; // Pega o ID do item encontrado
        AddToSystemJournal('Item encontrado! Saqueando...');
        MoveItem(item, FindQuantity, Backpack, 1, 1, 0);
        Wait(200); // Aguarda um pouco entre as ações para não sobrecarregar o servidor
      end;
    end;
    Ignore(corpse); // Ignora o corpo para não verificar novamente
  end;
end;

begin
  // Loop infinito para continuar verificando e saqueando corpos indefinidamente
  while True do
  begin
    loot; // Chama a procedure loot a cada iteração do loop
    Wait(200); // Aguarda 1 segundo (1000 milissegundos) antes da próxima iteração
  end;
end.
