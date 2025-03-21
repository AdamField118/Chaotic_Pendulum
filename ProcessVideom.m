function [t,theta]=ProcessVideom(filename);
vid= VideoReader([filename,'.AVI']);
numFrames=vid.NumberofFrames
%imarray=read(vid,[1 numFrames]);
fram2read=1:round(0.01*numFrames):numFrames;
for k=1 : length(fram2read)
    grayimg(:,:,k)=rgb2gray(read(vid,fram2read(k)));
end
mimg=max(grayimg,[],3);
imshow(mimg,[])


%Draw a region to include only the top light
title('Draw a rectangle to include only the trace of the top light')
disp('Draw a rectangle to include only the trace of the top light')
% up_rect=round(getrect);
bwu=roipoly(mimg);

%Draw a region to include only the lower light
title('Draw a rectangle to include only the trace of the lower light')
disp('Draw a rectangle to include only the trace of the lower light       \n')
% low_rect=round(getrect);
bwl=roipoly(mimg);

%subimgu=grayimg(up_rect(2):up_rect(2)+up_rect(4), up_rect(1):up_rect(1)+up_rect(3),:);
%subimgl=grayimg(low_rect(2):low_rect(2)+low_rect(4), low_rect(1):low_rect(1)+low_rect(3),:);

for k=1 : numFrames
   fprintf( '\b\b\b\b\b\b\b\b\b\b\b%05i/%05i', k,  numFrames  );
   gimg=rgb2gray(read(vid,k)); 
%    subimgu=gimg(up_rect(2):up_rect(2)+up_rect(4), up_rect(1):up_rect(1)+up_rect(3));
%    subimgl=gimg(low_rect(2):low_rect(2)+low_rect(4), low_rect(1):low_rect(1)+low_rect(3));
   subimgu=double(gimg).*bwu;
   subimgl=double(gimg).*bwl;
   %mask_u = imresize(bwu, size(gimg));
   %mask_l = imresize(bwl, size(gimg));
   %subimgu = double(gimg).*mask_u;
   %subimgl = double(gimg).*mask_l;
   timg=subimgu;
   bims=(timg>(max(timg(:)-15)));
   s=regionprops(bims,'centroid');
   posv=[];

   for i=1:length(s)
    posv=[posv;s(i).Centroid(1) s(i).Centroid(2)];
   end
   posva=sortrows(posv,2);
   x_up(k)= posva(1,1);
   y_up(k)= posva(1,2);
   timg=subimgl;
   bims=(timg>(max(timg(:)-20)));
   s=regionprops(bims,'centroid');
   posv=[];
   for i=1:length(s)
   posv=[posv;s(i).Centroid(1) s(i).Centroid(2)];
   end
   posva=sortrows(posv,-2);
   x_low(k)=posva(1,1);
   y_low(k)=posva(1,2);

end
% 
% x_up=x_up+up_rect(1)-1;
% y_up=y_up+up_rect(2)-1;
% x_low=x_low+low_rect(1)-1;
% y_low=y_low+low_rect(2)-1;
theta=atan2(y_low, x_low);
t=(0:length(theta)-1)/vid.FrameRate;
close all;
figure,plot(t,theta,'-o')
save([filename,'.mat'],'t','theta')