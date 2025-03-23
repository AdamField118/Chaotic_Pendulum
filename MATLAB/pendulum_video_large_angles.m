function pendulum_video_large_angles
%video analysis for physical pendulum
%this program will process a movie of the pendulum and determine the amplitude, damping constant, phase,
%and angular velocity of the oscillation.
%The user inputs include the AVI_name, the range and stepsize of frames to
%analyze. Also need to set the ROI, which here is the 
%center, radii which contain the paths of the lights and others.
%Input paragraphs are delimited using %************************
% It saves
% 1) the figure showing the oscillation and its fitting as AVI_name.fig
% 2) the oscillation and fitting parameters as as AVI_name.mat

%note if the movie has been analyzed, and if a .mat file exists, then the
%program will skip loading in the movie and go straight to the analysis
%section
clear all
%inputs are here
%************************
AVI_name = '..\Videos\DSC_0046';
%***********************
if ~exist( strcat( AVI_name, '.mat' ) )

% Process the video without ploting the dots on images. You will be asked
% to specify the starting frame, interval and ending frame. if you want to
% process the whole video without 
  [t, theta]=ProcessVideom(AVI_name);
else
    load( strcat( AVI_name, '.mat' ) );

end
    clf;
    plot( t, theta, '-.' );
    ylabel( '\theta' );
    xlabel( 't (sec)' );
 title('Click on the point where the first maximal angle is located')  
 [tstart,thetst]=ginput(1);
 
 ids=find(t>tstart);
 tfit=t(ids)-t(ids(1));
 thetafit=theta(ids);
 
 
 %t_intersec = intersections(tfit,thetafit-mean(thetafit),tfit([1 end]),[0 0]', 'ROBUST');
 [xi, yi] = polyxpoly(tfit, thetafit-mean(thetafit), [tfit(1) tfit(end)], [0 0]);
 t_intersec = xi;

%% determining times of the local extrema (which occur when the time derivate of theta is zero)
%t_diff_theta_intersec = intersections( tfit(1:end-1), diff( thetafit ),tfit([1 end]),[0 0]', 'ROBUST');
[xi, yi] = polyxpoly(tfit(1:end-1), diff(thetafit), [tfit(1) tfit(end)], [0 0]);
t_diff_theta_intersec = xi;
%% determining the amplitude of the extrema
[amplitude, T] = deal( abs( interp1( tfit, thetafit-mean(theta), t_diff_theta_intersec ) ), 2*diff(t_intersec) );


%Find the frequency of small angle oscs,using the last 10 oscillations.

if length(t_intersec) > 21
idsmall=find(tfit>t_intersec(end-21));
idss=find(tfit>t_intersec(end-20));
tst=tfit(idsmall);
thetas=thetafit(idsmall);
%thetast=thetafit(idsmall:idss);
thetast = thetafit(idsmall(1):idss(1));
[ym,idst]=max(thetast);

%tsmall=tst(idst:end)-tst(idst);
%theta_small=thetas(idst:end);
tsmall = tst(idst:end) - tst(idst);
theta_small = thetas(idst:end);
%--------
%fitparam=fitdecayosc(tsmall,theta_small);
% Define your decaying sine model:
% p(1)=A (amplitude), p(2)=λ (decay constant), p(3)=ω (angular frequency), p(4)=φ (phase)
model = @(p,t) p(1) * exp(-p(2)*t) .* sin(p(3)*t + p(4));

% Provide an initial guess for the parameters
p0 = [max(theta_small), 0.1, 2*pi/mean(diff(tsmall)), 0];

% Fit the model using lsqcurvefit (requires Optimization Toolbox)
options = optimoptions('lsqcurvefit','Display','off');
p_fit = lsqcurvefit(model, p0, tsmall, theta_small, [], [], options);

% Package the parameters into a structure similar to fitdecayosc output
fitparam.amp = p_fit(1);
fitparam.decayt = p_fit(2);
fitparam.freq = p_fit(3)/(2*pi);  % convert angular frequency to frequency (Hz)
fitparam.phase = p_fit(4);
%---------
theta0=fitparam.amp;
%omega0=sqrt((2*pi*fitparam.freq)^2+1/(fitparam.decayt)^2);
omega0=2*pi*fitparam.freq;
Tfit=2*pi/omega0;
close all
figure(1)
p = plot( t, theta, '-' );
ylabel( '$\theta$', 'interpreter', 'latex' );
xlabel( '$t$ (sec)', 'interpreter', 'latex' );
axis tight;
figure(2)
plot( amplitude(1:min(length(amplitude), length(T))), T(1:min(length(amplitude), length(T))), '.' );
hold on;
% this is the function for the dependence of period on swing amplitude
fnc4amplitude = @(amplitude) 1 + (1/2)^2*sin(amplitude/2).^2 + (1*3/2/4)^2*sin(amplitude/2).^4 + (1*3*5/2/4/6)^2*sin(amplitude/2).^6 + (1*3*5*7/2/4/6/8)^2*sin(amplitude/2).^8 + ...
    (1*3*5*7*9/2/4/6/8/10)^2*sin(amplitude/2).^10 + (1*3*5*7*9*11/2/4/6/8/10/12)^2*sin(amplitude/2).^12 + (1*3*5*7*9*11*13/2/4/6/8/10/12/14)^2*sin(amplitude/2).^14 + ...
    (1*3*5*7*9*11*13*15/2/4/6/8/10/12/14/16)^2*sin(amplitude/2).^16 + (1*3*5*7*9*11*13*15*17/2/4/6/8/10/12/14/16/18)^2*sin(amplitude/2).^18 + ...
    (1*3*5*7*9*11*13*15*17*19/2/4/6/8/10/12/14/16/18/20)^2*sin(amplitude/2).^20 + (1*3*5*7*9*11*13*15*17*19*21/2/4/6/8/10/12/14/16/18/20/22)^2*sin(amplitude/2).^22;
%legend( plot( 0:0.01:max(amplitude), Tfit/fnc4amplitude(theta0)*fnc4amplitude(0:0.01:max(amplitude)), '-r' ), 'T = 1 + (1/2)^2 \sin(\theta_0/2)^2 + (1*3/2/4)^2 \sin(\theta_0/2)^4 + ...' );
plotHandle = plot(0:0.01:max(amplitude), Tfit/fnc4amplitude(theta0)*fnc4amplitude(0:0.01:max(amplitude)), '-r');
legend(plotHandle, '$T = 1 + \left(\frac{1}{2}\right)^2\sin\left(\frac{\theta_0}{2}\right)^2 + \left(\frac{1\cdot3}{2\cdot4}\right)^2\sin\left(\frac{\theta_0}{2}\right)^4 + \dots$', 'Interpreter', 'latex');
xlabel( 'Amplitude, $\theta_0$', 'interpreter', 'latex' );
ylabel( '$T$ (sec)', 'interpreter', 'latex' );
hold off
%%

%this is the term B = b\omega_0 /2. For your write-up convert this to b,
%and discuss b.
B = -diff( log( amplitude((1:min(length(amplitude), length(t_intersec)))) ) )./diff( t_intersec((1:min(length(amplitude), length(t_intersec)))) );
figure(3)
plot( amplitude(1:numel(B)), B, '.' );
xlabel( '$\theta_0$', 'interpreter', 'latex' );
ylabel( '$B$  (1/sec)', 'interpreter', 'latex' );
else
   Disp('Not enough data points, please take a video with longer duration') 
end