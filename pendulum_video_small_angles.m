function pendulum_video_small_angles
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

%************************
AVI_name = '..\Videos\DSC_0045';
%***********************
if ~exist( strcat( AVI_name, '.mat' ) )
    % Process the video (ProcessVideom must be on your path)
    [t, theta] = ProcessVideom(AVI_name);
else
    load( strcat( AVI_name, '.mat' ) );
end

clf;
plot(t, theta, '-.');
ylabel('\theta');
xlabel('t (sec)');
title('Click on the point where the first maximal angle is located');
[ts, thets] = ginput(1);
tstart = ts;
%tend = ts(2);
%ids = find(t>tstart & t<tend);
ids = find(t > tstart);
tcut = t(ids);
thetacut = theta(ids);
[~, idst] = max(thetacut);

tfit = tcut(idst:end) - tcut(idst);
thetafit = thetacut(idst:end);
toffset = tcut(idst);

%%
% Instead of using fitdecayosc (which is not built-in), we use lsqcurvefit to fit
% a decaying sine model:
%   y(t) = A * exp(-lambda*t) * sin(omega*t + phi) + offset
% where:
%   p(1) = A (amplitude)
%   p(2) = lambda (decay constant)
%   p(3) = omega (angular frequency)
%   p(4) = phi (phase shift)
%   p(5) = offset (vertical shift)

model = @(p, t) p(1) * exp(-p(2)*t) .* sin(p(3)*t + p(4)) + p(5);
p0 = [max(thetafit), 0.1, 2*pi/mean(diff(tfit)), 0, 0];  % initial guess
options = optimoptions('lsqcurvefit','Display','off');
p_fit = lsqcurvefit(model, p0, tfit, thetafit, [], [], options);

% Package the fitted parameters into a structure (similar to fitdecayosc output)
fitresl.amp    = p_fit(1);
fitresl.decayt = p_fit(2);
fitresl.freq   = p_fit(3) / (2*pi); % convert angular frequency to Hz
fitresl.phs    = p_fit(4);
fitresl.vshift = p_fit(5);

theta0 = fitresl.amp;
omega0 = sqrt((2*pi*fitresl.freq)^2 + 1/(fitresl.decayt)^2);
offset = fitresl.vshift;
phi = fitresl.phs;
b = (1/fitresl.decayt) * (2/omega0);

figure(1);
savefig(strcat(AVI_name, '.fig'));

save(strcat(AVI_name, '.mat'), 'toffset', 'tfit', 'thetafit', 'b', 'omega0', 'offset', 'phi', 'theta0', 'fitresl', '-append');

return;
