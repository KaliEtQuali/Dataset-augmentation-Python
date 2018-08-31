cam = webcam('Logicool HD Webcam C270')
%%
preview(cam)
%%
pause(3)
cam.Brightness = 150;
cam.Resolution= '960x720';
saveDir = fullfile(pwd, 'capture', 'test2', 'internal');
mkdir(saveDir)  
figure
for idx = 1:100
   % Acquire a single image.
   rgbImage = snapshot(cam);

   fileName = num2str(idx, 'img%04d.jpg');
   savePath = fullfile(saveDir, fileName);

   imwrite(rgbImage, savePath)
   % Display the image.
   imshow(rgbImage);
   drawnow
   pause(0.5)
end
close
%%
path = 'C:\Users\s1358\PycharmProjects\test_aruco\capture\yellow3\external'
cam.Brightness = 150;
cam.Resolution= '960x720';
saveDir = fullfile(path,'desk','ver');
mkdir(saveDir)  
figure
for idx = 1:200
   % Acquire a single image.
   rgbImage = snapshot(cam);

   fileName = num2str(idx, 'img%04d.jpg');
   savePath = fullfile(saveDir, fileName);

    imwrite(rgbImage, savePath)
    % Display the image.
    imshow(rgbImage);
    title(idx,'FontSize',20)
    drawnow
    pause(0.2)
    end
close