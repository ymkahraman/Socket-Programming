%Yusuf Mert Kahraman 2304830
%Server MATLAB
server = tcpserver("localhost", 4000);
fopen(server);
Index = [0;1;2;3;4;5;6;7;8;9];
Data = [0;10;20;30;40;50;60;70;80;90];
while true
    if(server.NumBytesAvailable > 0)
        command = read(server,server.NumBytesAvailable,'string');
        disp("Received message (from proxy to server): " + command)
        dataSplit = split(command,[";"]);
        opcode = split(dataSplit(1),["="]);
        indexcode = split(dataSplit(2),["="]);
        opcode = opcode(2);
        switch opcode
            case "GET"
                % Here is used for both GET and ADD operations.
                indexcode = indexcode(2);
                indexdata = Data(str2num(indexcode) + 1);
                if(~isnan(indexdata))
                    n = "OP=GET;" + dataSplit(2) + ";DATA=" + string(indexdata);
                else
                    n = "OP=GET;" + dataSplit(2) + ";DATA=NO_DATA";
                end
                disp("Delivered message (from server to proxy): " + n)
                fwrite(server,n);
            case "PUT"
                indexcode = indexcode(2);
                indexdata = split(dataSplit(3),["="]);
                indexdata = indexdata(2);
                Data(str2num(indexcode) + 1) = str2num(indexdata);
                M = [Index Data];
                M = array2table(M,"VariableNames",["Index","Data"]);
                disp(M)
                n = command + ";DONE";
                disp("Delivered message (from server to proxy): " + n)
                fwrite(server,n)
            case "CLR"
                %NaN means DATA is deleted (empty.)
                for i = 1:10
                    Data(i) = NaN;
                end
                n = "OP=CLR;DONE";
                disp("Delivered message (from server to proxy): " + n)
                fwrite(server,n)
                M = [Index Data];
                M = array2table(M,"VariableNames",["Index","Data"]);
                disp(M)
        end
    end
end

