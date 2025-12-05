# Table of Contents

<ol>
  <summary><a href="#overview">Overview</a></summary>
  <details>
  <summary><a href="VideoProcessing/README.md">Video Processing</a></summary>
    <ol>
      <details>
      <summary><a href="VideoProcessing/README.md#motivation">Motivation</a></summary>
        <ol>
          <details>
          <summary><a href="VideoProcessing/README.md#dev-process">Dev Process</a></summary>
            <ol>
              <summary><a href="VideoProcessing/README.md#start">Start</a></summary>
              <details>
              <summary><a href="VideoProcessing/README.md#decoding-chaotic-tracking">Decoding Chaotic Tracking</a></summary>
                <ol>
                  <summary><a href="VideoProcessing/README.md#color-differentiation">Color Differentiation</a></summary>
                  <summary><a href="VideoProcessing/README.md#previous-frame-proximity">Previous Frame Proximity</a></summary>
                </ol>
              </details>
              <summary><a href="VideoProcessing/README.md#camera-setting">Camera Setting</a></summary>
            </ol>
          </details>
        </ol>
      </details>
      <summary><a href="VideoProcessing/README.md#how-to-use-the-code">How to Use the Code</a></summary>
      <summary><a href="VideoProcessing/README.md#results">Results</a></summary>
    </ol>
  </details>
  <details>
  <summary><a href="Simulations/README.md">Simulation</a></summary>
    <ol>
      <summary><a href="Simulations/README.md#plan">Plan</a></summary>
      <details>
      <summary><a href="Simulations/README.md#mathematical-model">Mathematical Model</a></summary>
        <ol>
          <summary><a href="Simulations/README.md#setting-up-the-lagrangian">Setting up the Lagrangian</a></summary>
          <summary><a href="Simulations/README.md#euler-lagrange-equations">Euler-Lagrange Equations</a></summary>
          <summary><a href="Simulations/README.md#final-equations">Final Equations</a></summary>
        </ol>
      </details>
      <details>
      <summary><a href="Simulations/README.md#the-code">The Code</a></summary>
        <ol>
          <details>
          <summary><a href="Simulations/README.md#config">Config</a></summary>
            <ol>
              <details>
              <summary><a href="Simulations/README.md#params">Params</a></summary>
                <ol>
                  <summary><a href="Simulations/README.md#solver">Solver</a></summary>
                </ol>
              </details>
            </ol>
          </details>
          <details>
          <summary><a href="Simulations/README.md#equations-of-motion">Equations of Motion</a></summary>
            <ol>
              <summary><a href="Simulations/README.md#parameters-and-state-extraction">Parameters and State Extraction</a></summary>
              <summary><a href="Simulations/README.md#intermediate-calculations">Intermediate Calculations</a></summary>
              <summary><a href="Simulations/README.md#return-value">Return Value</a></summary>
            </ol>
          </details>
          <summary><a href="Simulations/README.md#solve-pendulum-ode">Solve Pendulum ODE</a></summary>
          <summary><a href="Simulations/README.md#create-animation">Create Animation</a></summary>
          <summary><a href="Simulations/README.md#process-pendulum-data">Process Pendulum Data</a></summary>
          <summary><a href="Simulations/README.md#graphing-functions">Graphing Functions</a></summary>
          <summary><a href="Simulations/README.md#main">Main</a></summary>
        </ol>
      </details>
      <summary><a href="Simulations/README.md#results">Results</a></summary>
    </ol>
  </details>
  <details>
  <summary><a href="Verification/README.md">Verification</a></summary>
    <ol>
      <summary><a href="Verification/README.md#goal">Goal</a></summary>
      <details>
      <summary><a href="Verification/README.md#the-code">The Code</a></summary>
        <ol>
          <details>
          <summary><a href="Verification/README.md#fourier-functions">Fourier Functions</a></summary>
            <ol>
              <details>
              <summary><a href="Verification/README.md#fourier_series">fourier_series</a></summary>
                <ol>
                  <summary><a href="Verification/README.md#parameters">Parameters</a></summary>
                  <summary><a href="Verification/README.md#function-description">Function Description</a></summary>
                </ol>
              </details>
              <details>
              <summary><a href="Verification/README.md#fit_fourier">fit_fourier</a></summary>
                <ol>
                  <summary><a href="Verification/README.md#Parameters-1">Parameters</a></summary>
                  <summary><a href="Verification/README.md#function-description-1">Function Description</a></summary>
                </ol>
              </details>
            </ol>
          </details>
          <details>
          <summary><a href="Verification/README.md#graphing-functions">Graphing Functions</a></summary>
            <ol>
              <summary><a href="Verification/README.md#plot_fourier_comparison">plot_fourier_comparison</a></summary>
              <summary><a href="Verification/README.md#plot_deviation">plot_deviation</a></summary>
            </ol>
          </details>
        </ol>
      </details>
      <summary><a href="Verification/README.md#results">Results</a></summary>
    </ol>
  </details>
  <summary><a href="#poster">Poster</a></summary>
  <summary><a href="#credits">Credits</a></summary>
</ol>

# Overview  

In Intermediate Physics Laboratory (2025) we have a project to analyze a chaotic pendulum system. This will be done through tracking the angles of a physical set up, making a theoretical model, then comparing the results of the two.  

Here is an image of the physical setup we are working with:  

<div asummarygn="center">
  <img src="./Assets/physical_setup.png" alt="Setup" width="90%">
  <p>Figure 1. Physical Setup.</p>
</div>

The MATLAB code given to us for tracking LEDs in a video was broken, old, and quite frankly bad, so we developed a new solution using openCV and other python summarybraries. See [this README](VideoProcessing/README.md).  

We also used Lagrangians to make a theoretical model, then we simulated the model. See [this README](Simulations/README.md).  

If you are a future group doing this lab and hope to code something cool, consider forking this repository!  

# Poster  

Here is a poster of our progress made for the first lab of IPL:  

<div asummarygn="center">
  <img src="./Assets/Adam and Chris - Modesummaryng of a Chaotic Pendulum.png" alt="Poster" width="90%">
  <p>Figure 2. Project Poster!</p>
</div>

# Presentation   

The presentation in class went well! Here is the [slides we used](Assets/Adam%20and%20Chris%20-%20Chaotic%20Pendulum%20Presentation.pdf).

# Credits  

Made by Adam Field and Christopher Pacheco.  
Thank you Professor Noviello and TAs Drew and Holden for all the help.