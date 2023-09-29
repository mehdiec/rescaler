def create_sap_parameters(
    sr,
    piv,
    vm,
    ffpb,
    ct,
    aot,
    path_animaprocess="/home/polina/Documents/GitHub/AnimalProcessing",
):
    content = f"""% SingleAnimalProcessing parameters (SAP_parameters)
%
% Script where ALL program parameters are specified. This enables to easily
% process several movies of different animals using the exact same
% parameters.
%
% Version 8.9
% Boris Guirao  
addpath(genpath("{path_animaprocess}"));

%% PROGRAMS TO RUN %%

% PRE-segmentation
TR =    0;                                  % "TimeRegistration" (NO PARAMETERS) (7.12) 
SR =    {sr};                                  % "SpaceRegistration" (1 PARAMETER: clicktime) (7.12) 
PIV =   {piv};                              	% "ParticleImageVelocimetry"
GEP =   0;                                  % "GeneExpressionPattern" (GR<ID reguired)
VM =    {vm};                                  % "VelocityMaps" (with modeVM = 'PIV' OR after cell tracking with modeVM = 'CT')

% POST-segmentation
FFPB =  {ffpb};                                  % "FilterFourPixelBlocks" (NO PARAMETERS)
SIA =   0;                                  % "SegmentedImageAnalysis"
CT =    {ct};                                  % "CellTracking" (NO PARAMETERS)(7.8)
HC =    0;                                  % "HolesCorrection" (NO PARAMETERS) (8.8)
CTD =   0;                                  % "CellTrackingDisplay"
CPT =   0;                                  % "CellPatchTracking"
CTA =   0;                                  % "CellTrackingAnalysis" (can also run before CPT in full image mode)
AOS =   0;                                  % "AverageOverSpace"
TA =    0;                                  % "TensorAnalysis"

% Force inference
GV =    0;                                  % "GetVertex" (NO PARAMETERS)
STPE =  0;                                  % "STPEstimate"
MSM =   0;                                  % "MatlabShujiMatcher"
SM =    0;                                  % "StressMap"

% Time averaging
AOT =   {aot};                                  % AverageOverTime
POT =   0;                                  % PlotOverTime (8.6)

% NB: 
% - programs are listed in their order of execution
% - CTD can run without SIA backups, but they are required to make New Junctions and SIA division backups
% - "NO PARAMETERS" means no SPECIFIC parameters for this program, but will use common parameters.


%% MAIN COMMON PARAMETERS %%

% GRIDSIZE SPECIFICATION (XS, S, M, L, XL). Will specify gridsize to use for PIV, cell tracking and to name folders (moved here 8.6)
PIVgrid = 'L';              

% CPT filtering of cells. 0: no filtering; 
excludeLostCells = 2;
% 1: excluding cells getting lost OR losing ALL daughters;
% 2: excluding cells losing 1+ daughter (moved 7.6)

 % CTD parameter: in hours, minimal time to allow a new division (does NOT apply to first divisions) (7.5)
minCycleDuration = 3;      
    
% Clone related:
cloneTracking = false;      % To track clone parts of tissue AND their WT symmetric counterparts (% midline) (7.0)
nCellsMin = 10;             % number of cells below which a clone part is not analyzed (CPT)

% Grid related:
gridType = 'E';             % '' (full image processing),'E' (Eulerian grid) or 'L' (Lagrangian)
gridOverlap = 0.5;            % specifies fraction of overlap between boxes
gridTime = 'start';         % time APF to draw grid to determine cell patches to track. Can also be "start" or "final". ONLY relevant for LGrids (6.7).

% NB: if cloneTracking = true, "gridTime" will be overridden by "cloneMaskTime" which is determined by "cloneMaskFrame" that is either directly specified in SAP_info or
% that is extracted from the last characters of "path2cloneMask". In other words, the frame (=> time) corresponding clone mask determines the time at which it is applied.

plotType = 'split+';        % "merged" (ellipse), "split+"/"split-" (circle & dev+/- parts), "circle", "dev+" and "dev-" 
clickTime = '21h40';   % time at which image was clicked to determine macrochaetes 


%% ADDITIONAL COMMON PARAMETERS %%

CustomColors ;                       % defines usual set of colors

% Cell Tracking related
timeB4Del = 2;                      % time (hours) during which A/D cells are tagged before delamination (CTD & CPT).
                                    % NB: "Inf" will tag them or their ancestor from the beginning of the movie.
displayCellNumbers = false;         % for CT, CTD, CPT
fontSizeCellNumbers = 4;            % font size of cell numbers, when displayed

% Colors of cell categories:
colorBorderCells = grey;    % usually "grey" (Potts) or "custom_white" (regular images)
colorFLCells = light_grey;          % usually "light_grey", Denis: light_dark_green
colorFusion = mid_red;              % usually "mid_red"
colorNewCells = dark_purple;        % usually "dark_purple"
colorApoptosis = dark_grey;         % usually "dark_grey"
colorMacrochaetes = yellow;         % usually "yellow" (6.9)
colorJunctions = grey;              % color of membrane pixels (7.5)

% Related to newly formed junctions (CTD & CPT) (7.5)
displayNewT1Junctions = false;        	% to display new junctions formed by T1s
displayNewDivJunctions = false;       	% to display new junctions formed by DIVISIONS
displayNewDelJunctions = false;          % to display new junctions formed by DELAMINATIONS
newJuncDisplayTimes = [0 Inf];           % time hAPF (row vector) at which the display of new junctions starts, changes, and stop (last value, can be "Inf") (7.5)
colorNewT1Junctions = magenta;         % usually "magenta" (7.5)
colorNewDivJunctions = green;          % usually "green" (7.5)
colorNewDelJunctions = black;          % usually "black" (8.6)
% NB: new junction display requires SIA BACKUPS. "colorNewT1Junctions" should have one less color value than elements of "newJunctionStartTime"

% Tensor related (6.0)
signOpacities = [0.8 0.3];          % ONLY relevant for "split+/-" and "circle" display types: specifies opacity of positive(white) and negative(black) disks, respectively.
lineWidth = 1.5;                    % for circle, bars and ellipses (1.5 ok with BIG movies)
normalizeMethod = 'mean';            % Using either 'min','mean' or 'max' of raw AreaRatios BULK values to renormalize them ALL with "Normalizer".
EVstyles = {{'-' ':'}};               % ONLY relevant for "merged" display type: styles to display ellipse axes representing tensor eigenvalues (default {'-' ':'})

% Grid/Clone related (6.0)    
nLayers = 1;                        % **LAGRANGIAN ONLY**: number of layers to remove to define the bulk of the animal. Used nLayers = 3 for eLife formalism analysis.
                                    % NB: irrelevant when gridType runs in full image mode (1 single compartment) or with Eulerian grid
gridValidation = false;              % if = 1, asks user to validate grid
gridBulkThreshold = 0.1;             % will only display grid compartments with AreaRatios > bulkThreshold (Adrien )
gridDisplay = false;                 % Lagrangian grid ALWAYS displayed (6.0)
gridColor = cyan;
gridLineWidth = 1;                  % only matters for Egrid, Lgrid thickness specified in LGridPlotter
gridNumberColor = custom_white;     % color used to display patch/clone numbers onto CPT images (magenta used on grid image or clone masks) (8.6)

% Display and resolution (5.3):
colorInfo = black;
minimalInfoDisplay = false;         % if true, will only display hAPF and scalebar
imageFormatOutput = 'png';          % 'png', 'pdf' (for vector objects) or 'svg' (AOT only,supports transparency of vector objects) (5.2)
                                    % NB: 'svg' must be set in AOT section
displayImages = 'off';               % "'on' to display the figures 'off' to save them without showing them in AOT, AOA, DBA

                                    
                                    
% Creation of a results folder (used by AOT) (8.3):
resultsFolder = '';


%% AOT Parameters (mod 6.8) %%

% NB: parameters are also relevant for "VelocityMaps" execution (8.2)

% averageOverAll = {{ 'VM' ; 'TA'; 'AOS'; 'SM'}};  % ALL programs over which average will be run (6.8)
averageOverAll = {{'VM'}};
% NB: ALWAYS LIST "SM" FIRST, OTHERWISE THE MISSING FRAMES FROM STPE WILL ALSO APPEAR AS MISSING FOR AOS,TA AND !


% double specifying width of time sliding average IN HOURS (will be converted into frame number)
timeWidthAll = [Inf; 2; 4]; 
% NB: if empty OR "Inf", timeWidth will be set to its MAXIMAL value, namely timeStart-timeStop (and "timeOverlap" will be forced to 0)
% NB: if set to 0, no averaging will be made ("noAverage" mode) and corresponding "timeOverlap" will be forced to 0 as well.

% FRACTION of time overlap of time sliding average (in [0, 1[)
timeOverlapAll = [0; 1-dt/(60*timeWidthAll(2)); 1-dt/(60*timeWidthAll(3))];


% To plot or no plot 
% NB: average is ALWAYS done using alltime_backup
makePlotsAllAOT = [0; 1; 0];


% Timepoints between which averages will be made. if empty, will use full time span specified by ACTUAL Start/Final frames
timeStart = '14h00';               
timeStop = '32h00';

% Will load backups and stack tensors matrices/cell arrays over time into "all_time_..." 4D matrix and use it to calculate time averages:
% NB: REuses plot parameters defined in the program section

forceEGrid = false;                 % forces plot on Eulerian grid. Only relevant when calculations were made on lagrangian grid (5.2)
saveSVG = false;


%% POT Parameters (mod 8.6) %%

%%% list of grid/clone compartments to average over and plot over time
% COMP zones BIGwt2
boxIJs{{1}} = [1 1 ; 2 1];
boxIJs{{2}} = [4 1 ; 5 1];
boxIJs{{3}} = [7 1 ; 6 1];
boxIJs{{4}} = [9 1 ; 8 1];
boxIJs{{5}} = [3 1];
boxIJs{{6}} = [10 1];

plotTypePOT = 'inst';        % "inst" or "cum" for cumulative
plotRenormPOT = 'renorm';   % "raw" or "renorm", all curves absolute max are reset to 1

Qs2Plot.iso =   {{'EG', 'ED', 'ES', 'ER', 'EA'}};
% Qs2Plot.iso =   {{'dnD', 'rPatchArea','rCellArea', 'Epsilon', 'EG', 'ES', 'ER', 'EA'}};
Qs2PlotMax.iso =   { {}};           % WT COMMON


% Qs2Plot.iso =   {{'dnA/nCoreRNs', 'rPatchArea', 'PatchArea', 'U', 'rCellArea', 'CellArea'}};
% Qs2PlotMaxTF.iso = [      1,             1,           0,       1,      1,            1];
% Qs2PlotMax.iso = {{0.03,         0.14,            [],         6.5,      0.14,       59}};       % WT COMP
% Qs2PlotMax.iso = {{0.043,         0.04,           [],         6,       0.14,       52}};           % WT DEL
 
Qs2Plot.devDiag =   {{'EG', 'ED', 'ES', 'ER', 'EA'}};
Qs2PlotMax.devDiag = {{0.08}}; 
Qs2Plot.devOffDiag =   {{'EG', 'ED', 'ES', 'ER', 'EA'}};
Qs2PlotMax.devOffDiag = {{0.08}};

makePlotsAllPOT = [0;1];


%% PIV PARAMETERS %%

% Images to display and save -------------------------------------------------------------------------------------------------------
velocityDisplay = false;               % =1 Velocity_.png images will be saved, =0 they won't
PIVarrowColor = 'm';                   % Matlab color letters ('c','m','y'...) 7.7
speedDisplay = false;                  % =1 Speed_.png images will be saved, =0 they won't. Only possible with (u,v), not (uq,vq)
divergenceDisplay = false;             % =1 Divergence_.png images will be saved, =0 they won't. Only possible with (u,v), not (uq,vq)
%-----------------------------------------------------------------------------------------------------------------------


%% GEP PARAMETERS %% (stephane)

% ONLY WORKS WITH EULERIAN GRID

% normalize_GEP = false; % put true if not pre-treated in Fiji. If false, images must have had undergone: remove background + normalize in Fiji first
% percentage_GEP = 0.01; % to remove gaussian larger tail (only matters if normalize_GEP = true)

plotTensorsGEP = {{'Cad'}};

if exist('uniqueScaleRatio_GEP','var')
    scaleBarLengthGEP = uniqueScaleBarLength_GEP ;
    scaleRatioGEP =  uniqueScaleRatio_GEP;  
else
    scaleBarLengthGEP = 1;
    scaleRatioGEP =     {{3e2}};
    % quantities         ID               % NB: SHOULD ALWAYS BE LISTED IN THIS ORDER!!
end
killMeanTraceGEP = 0;


%% VM PARAMETERS (6.2) %%

% 'CT' to calculate data from TRACKING, 'PIV' to calculate it from PIV. (mod 8.2)
modeVM = 'PIV'; 

% PIV grid to be used by VM (can be different than PIVgrid). ONLY relevant in 'PIV' mode
PIVgridVM = 'L'; 

% Possible quantities to plot: 'U' ; 'EpsilonVM' ; 'OmegaVM'
plotTensorsVM = {{'U' 'Epsilon' 'Omega'}};    

takeImageNegative = true;

if ~exist('scaleRatioVM','var')
    % quantities           U   Epsilon   Omega      
    % NB: SHOULD ALWAYS BE LISTED IN THIS ORDER
    scaleRatioVM =        {{30    5e3      5e3   }};
    scaleBarLengthVM =    [5    0.02      0.02  ];
end

killMeanTraceVM = [0 0 0];


%% SIA PARAMETERS (7.8) %%

matlabSIA = 1;                   % if = 1, will run Matlab SIA instead of the C++ one (8.0)
noDisplay = 1;                   % if = 1, none of the display below will be saved)
noStatistics = 1;                % if = 1, none of the histograms or xls files below will be saved
allImagesInSameFoler = false;     % put all type of images in same folder (still sorting images according to Cells vs Sides) (6.9)
% Side thickness to estimate signal-------------------------------------------------------------------------------------------------
skelDilatation = 2;               % number of pixels used to dilate skeleton to calculate mean intensity of sides
skelDilatationBG = 4;             % number of pixels around side to determine background intensity (pixels involved in I side calculation are excluded). NB: take it to be (3+)*intDilatation
% NB: as of SIA 2.15, background intensity is ALWAYS removed from raw intensity values
% NB: as of SIA 3.0, "intDilatationBG" was decreased to 4 (instead of 6 before)
% BOX OPTIONS (SIAboxMode = 1) ----------------------------------------------------------------------------------------------------------
SIAboxMode = 0;                  % if = 1, SIA runs on a box. REQUIRES "SIA" BACKUP FILES!!!
reloadBox = 0;                   % will try to reload previously drawn box (in case segmentation got updated while the box is still valid) (useless if "replotSIA = 1")
predefinedBoxData = [];          % [Xtopleft Ytopleft Width Height] in pixels. only matters if "Predefined Box" is selected in box drawing interface (3.1a)
oneCellFrontier = 1;             % if = 1, the first layer will be 1 cell thick IN THE DRAWING FRAME; if = 0 (BUGS in 3.1, ALL cells crossed by the drawing line will be listed as First layer cells. 

% OUTPUT SELECTION -----------------------------------------------------------------------------------------------------

%%% STATISTICS (saving of histograms and xls files):
cellStatistics = 1;
sideStatistics = 1;
vertexStatistics = 1;

%%% CELLS
%-------------------------------------------------------------------------------
displayRNsAndVs = 0;                % will display region numbers and vertices
circleSize = 2;                     % specifies circle size around vertices.
circleWidth = 0.5;                  % specifies circle line width
%%%% Areas:----------------------------------------------------------------
displayArea = 0; 
% rangeArea = [];
% rangeArea = [10 400]; % MARTIAL
% rangeArea = [6 19];                % values set for frame 240 of BIG
rangeArea = [6 55];              % ** IN um **: OUTSIDE this window, cells will be displayed in dark BLUE/RED. If left empty (ie []), color display spanning [min_area max_area]. Dachs study: [8 60]
%%%% Anisotropies:---------------------------------------------------------
displayAnisotropy = 1;   
% rangeAnisotropy = [0.2 0.7]; % MARTIAL
rangeAnisotropy = [0.2 0.5];       % ** 0 < value < 1 **: OUTSIDE this window, cells will be displayed in dark GREEN/ORANGE. If left empty (ie []), color display spanning [min_anis. max_anis]. Dachs study: [0.1 0.6]
%%%% Neighbors:------------------------------------------------------------
displayNeighbor = 0;               
%%%% CHORD disorders:-----------------------------------------------
displayChordDisorder = 0;
rangeChordDisorder = [0.1 0.7];          % 0.3 0.6
% rangeChordDisorder = [0 0.7];          % 0.3 0.6      
%%%% Side intensity disorders:---------------------------------------------
displaySideIntensityDisorder = 0;      
rangeSideIntensityDisorder = [0.1 0.4];     % 0.08 0.20
% rangeSideIntensityDisorder = [0.1 0.3];   % 0.08 0.20
%%%% Polarity Modes:-------------------------------------------------------                                                     
displayPolarityMode = 0;
% Display parameters:
displayCellMode0 = 0; % if =1 will display ellipse
displayCellMode1 = 0;
displayCellMode2 = 1;
modeScale = 4;
polarityScaleBarLength = 10; % intensity of polarity scale bar
mode1Color = 'cyan';
mode2Color = 'magenta';
polarityLineWidth = 1.5;
%-------------------------------------------------------------------------------

%%% SIDES
%-------------------------------------------------------------------------------
%%%% Chord lengths:
displayChordLength = 0;
rangeChordLength = [];
% rangeChordLength = [1 5];
%NB: for pten enter dimensionless chord lengths
%%%% Side intensities:
displayIntensity = 0;
rangeIntensity = [110 120];
%-------------------------------------------------------------------------------

%%% HISTOGRAMS
%-------------------------------------------------------------------------------
chordHistograms = 0;                 % range used is "chord_length_range"
neighborHistograms = 1;
nNeighborsMax = 11;                  % that will be plotted on histogram (2.0GMf)
%----------------------------------------------------------------------------------------


%% CTD PARAMETERS (6.0) %%

%%% CTD images:
makeCTDimages = false;                   % make classic CTD images (with shades of green) (6.9)
makeonlyCorrectionBackup = false;

colorDivision = [white_grey ; light_dark_green ; mid_dark_green ; dark_green; cyan]; % added extra tone (7.5)
% colorDivision = [white_grey ; white_grey ; white_grey ; white_grey; white_grey]; % NO DIVISION DISPLAY
% colorDivision = [custom_white ; light_dark_green ; mid_dark_green ; dark_green; 0.8*PLuc_green ; custom_cyan]; % added extra tone (7.5)
colorDivisionIssue = orange;            % color used for divisions occuring in less than "minCycleDuration"
colorDivisionDiscarded = magenta;       % color used for divisions yielding ONLY one sister
colorApoptosisIssue = crimson;          % color used for delaminating ANs that have a NON-CORE last RNs (because UNRELIABLE)

% Related to tracking fixes
displayJustDividedCellLinks = false;    % to display link between Just Divided Cells (in green). Link thickness is set by JDClineWidth below.
displayPatchedCellNumbers = false;
mFactor = 4;                            % magnification factor to display patched cell numbers: only matters if "displayPatchedCellNumbers" is true

%%% Del & Div grayscale images:
colorLevels = custom_white;             % Del & Div number will be shaded from black (lowest value) to "colorLevels" (highest)
% colorJunctions = 0.5*grey;                  % color of membrane pixels (7.5)
% colorLevels = [1 1 1] - dark_green;         % Del & Div number will be shaded from black (lowest value) to "colorLevels" (highest)

makeDivImages = false;                  % make division images (6.9)
% nDivMax = 2;                            % divion of: mother = 1; mother + both daughters = 3; mother + both daughters + 4 granddaughters = 7. Can be empty(6.9)
nDivMax = 7;                            % divion of: mother = 1; mother + both daughters = 3; mother + both daughters + 4 granddaughters = 7. Can be empty(6.9)

makeDelImages = false;                  % make delamination images (6.9)
nDelMax = 4;                            % delamination of: mother = 1; mother + both daughters = 3; mother + both daughters + 4 granddaughters = 7. Can be empty(6.9)

%%% All-time maps:
markerSize = 200;                   % size of apoptosis markers on global map
JDClineWidth = 2;                   % thickness of link between sister centroids
% Defining nTones for all-time CTD & CTA maps (7.5)
tMin = 14;              % min time in hours (color saturated below)
tMax = 40;              % max time (color saturated above)
tRange = tMax - tMin;   % one tone per half hour
nTones = 2*tRange + 1;  % +1 for background tone
% NB: the idea with "tMin" and "tMax" is not to change them often so different maps produced over different times and
% animals remain comparable


%% CPT PARAMETERS (7.2) %%

% NB: parameter "excludeLostCells" moved to "Main common parameters" section

% CLONE tracking related
greyLevelClone = 1;         % 1 to ONLY take clone parts inside BOTH ROIs (MT and WT); 0.4 to ONLY exclude clone parts outside of WT image (8.2)
matchingWTclone = 0;        % if 1, program will try to find WT counterparts to clone using symmetry % midline (7.2); if 2, just takes the WT parts complementary to clone parts (8.7)
                            % NB: clone parts (and WT ones respectively)
                            % are ONLY gathered together with "matchingWTclone" = 2 => CHOOSE THIS FOR ANIMAL AVERAGING WITH "MAP"!
invertCloneMask = false; 	% set to "true" when the clone is initally displayed in black instead of white (7.3)
colorClone = custom_blue; 	% color of clone parts
colorWT = light_dark_green; % IF matchingWTclone = true, color of WT parts matching clone parts
includeNewCells = true;   	% "true" is only relevant for tracking of a tissue part, NOT an actual clone with different genetic background!! (7.3)

% Display related
makeCPTimages = false;              % make classic CPT images (colored square patches or clones) (7.0)
singlePatchColor = '';       % to force all grid compartments to have same color (leave EMPTY otherwise). NB: overrides "keepPatchColors" (7.5)
% singlePatchColor = light_dark_green;       % to force all grid compartments to have same color (leave EMPTY otherwise). NB: overrides "keepPatchColors" (7.5)
keepPatchColors = true;             % if true AND "GridDef" backup already exists, will load existing patch colors (7.1)
midlineSymmetry = false;             % when even number of rows in grid, will symmetrize colors % midline. ONLY applies for grid (not clone) processing.
showNewCells = false;               % shows new cells with if true
showCoalescedCells = false;         % shows coalesced cells
showApoptoses = false;


%% CTA PARAMETERS (7.5)

% NB: CTD parameters above (tMin, tMax, tRange and nTones) are ALSO relevant for CTA.

% Related to bulk signal processing (8.6)
bulkSignalProcessing = false;
bulkSignalFilename = 'Casp_';
bulkSignalName = 'Casp';
signalMin = -10;
signalMax = 30;

% Data to plot
noDisplayCTA = false;        % if true, OVERRIDES below parameters

displayDeltaAngleData = false;
displayDeltaAreaData = true;
displayCellCycleData = true;
displayDelaminationData = true;

% Plot parameters
gridMapFrame = startFrame;              % frame used to plot grid maps (8.4)
averagingTimeRangeDivAngles = [0.5 1];  % In hours before division (7.7)
averagingTimeRangeDIV = [1 Inf];        % in hours before division for areas...
averagingTimeRangeDEL = [1 Inf];        % in hours before delamination for areas...

nDivThreshold = 2;              	% ONLY supports values 2 & 3!! Determines how many division rounds will be considered
removeB4DelHours = 2;              	% in hours, duration of data removal before delamination 
timeAfterDIVcutOff = 6;             % in hours, duration to stop recording sister area difference over time AFTER division
timeBeforeDELCutOff = 12;            % in hours, duration to stop recording sister area difference over time BEFORE delamination
yMaxTimeALD = 35;                	% for time plots showing sister apical area asymmetry After Last Division (ALD)

%circleScaleFactor = 50;     % magnification of circles
circleScaleFactor = 25;


%% AOS PARAMETERS %%

% Quantities to plot among "allQsAOS": 
plotTensorsAOS = {{ 'Epsilon'}}; % 'all', 'none' or 'Epsilon', 'Omega', 'U', 'M', 'I' , 'CDCad'.... 
% plotTensorsAOS = {{'dnD' 'dnA' 'rPatchArea' 'rCellArea'}}; % 'all', 'none' or 'Epsilon', 'Omega', 'U', 'M', 'I' , 'CDCad'.... 

imagePlotAOS = 'seg';       % 'raw' or 'seg'. Type of images to plot tensor contribution on (except for polarity always plotted on raw images). For 'raw', first raw image is picked.
% Scaling and scale bars:
scaleRatioAOS =     {{5       5e2   5e1  2.5   1      1        200         1          15e2       5    2e1   2e3     2e2       20   2e2    5e3    1e3     2e2  [10 10]  [20 200] [20 200] }};   % sets ratio setting size of ellipses or bars in tensor representation for M,I.
%scaleBarLengthAOS = [1e-2    1e-1  0.1   2    50    20       0.25        1e2         0.1       20     5   5e-2    1e-1       5   2e-1    1e-2   0.1     1e-1     2        2        2     ];   % scale bar lengths for each contribution     
scaleBarLengthAOS = [1e-2    1e-1  0.1   2    50    20       0.25        1e2         0.1       20     5   5e-2    1e-1        5   1e-1    5e-3   0.1     1e-1     2        2        2     ];   % scale bar lengths for each contribution     

killMeanTraceAOS =  [0        0     0    0    1      0         0          0           1         0     0      0       0       0     0       0     0       0       0        0        0     ];   % => mean trace = 0 in  plots (isotropic part = 0).
% allQsAOS =      PatchArea   Rho   I    M    V   CellArea  CellIaniso  nCoreRNs AreaDisorder  dnD   dnA   rRho  rPatchArea  U  Epsilon  Omega   R2  rCellArea  CDCad    CDEsg    CDMyo        % SHOULD BE LISTED LIKE IN "AllQsColorsUnits"!!


%% TA Parameters %%

% MAIN parameters ------------------------------------------------------------------------------------------------------ 
displayHLC = false;           % to plot Half Link Categorization using TA backups (replaced "replotTA" in 7.6).
                             % NB: to be used AFTER all TA backups have been generated. Create a fake last backup to bypass this check and run HLC display.
renormM = 'nLinks';          % "nLinks" (resp "nCells") will use number of LINKS (resp. CELLS) gained/lost by each process P for M renormalization (5.2)

% TENSOR display parameters---------------------------------------------------------------------------------------------
plotTensorsTA = {{'ES' 'ER' 'EG'  }}; 
% plotTensorsTA = {{'EG' 'ER' 'Phi' 'EGeig' }};    % list of tensors to plot. 
% plotTensorsTA = {{'EG' 'ES' 'ER' 'ED' 'EA' 'Phi'}};    % list of tensors to plot. 
skipTensorsTA = {{}};                            % list of tensors to skip in 
killMeanTraceTA = 0;

% Error display
errorPsMin = 1e-13;            % minimal value of error over to be shown, usually 10^(-10), Bigwt2(C++M): 10^(-2)  ARTICLE 1e-2
errorDnPsMin = 0;             % usually 0, Bigwt2(C++M): 10^(-1) ARTICLE 1e-1
errorFontSize = 8;

% HALF-LINK display parameters------------------------------------------------------------------------------------------
display_naHL = false;           % will also display HLs that are tagged "n/a" in all_HLC
HLstyles = {{'-' '--'}};          % prefer '--' with png, ':' with pdf (resolution doesn't matter then)
HLimageFormat = 'png';          % 'png' or 'pdf'
linkWidth = 1;                  % line width of links between cell centroids (0.3 for full thorax)

% SCALING parameters---------------------------------------------------------------------------------------------
if strcmp(plotType, 'dev+') || strcmp(plotType, 'dev-')
    % Anisotropic part:
    if ~exist('uniqueScaleRatioTA','var')
        scaleRatioTA = 15e3;                   % 2e3 for 2h average; 4e3 for 14h to 20h
        scaleBarLengthTA = 1e-2;            % sets scale bar lengths in the declared uits. 5*10^(-2) for 2h average; 2*10^(-2) for 14h
    
        srVector =       [ 1   1   1   3    1   1   1   1   1    1    1   1     1       1      1       1       1];
        sbVector =       [ 1   1   1  1/3   1   1   1   1   1    1    1   1     1       1      1       1       1];
%     % % MCatList =   {{'G';'S';'R';'Ds';'D';'A';'N';'F';'J';'Jb';'DM';'EU';'EGstar';'EPSI';'PhiU';'Ustar';'PhiUstar'}}
        scaleRatioTA = num2cell(scaleRatioTA*srVector);  % CELL ARRAY
        scaleBarLengthTA = scaleBarLengthTA*sbVector;    % VECTOR
    else
        scaleBarLengthTA = uniqueScaleBarLengthTA;
        scaleRatioTA = uniqueScaleRatioTA;
    end
    
elseif strcmp(plotType, 'circle')
    % Isotropic part:
    if ~exist('uniqueScaleRatioTA','var')
        scaleRatioTA = 15e3;                 % 4e3 for whole duration
        scaleBarLengthTA = 1e-2;            % sets scale bar lengths in the declared units. 2e-2 for whole duration
        
        srVector =       [ 1   1  1   1  0.33  1   1   1   1    1    1   1    1      1      1       1       1];
        sbVector =       [ 1   1   1   1    1   1   1   1   1    1    1   1    1      1      1       1       1];
        % % MCatList =   {{'G';'S';'R';'Ds';'D';'A';'N';'F';'J';'Jb';'DM';'E';'EPSI';'Phi';'dMoldC';'Ustar';'PhiUstar'}}
        scaleRatioTA = num2cell(scaleRatioTA*srVector);      % CELL ARRAY
        scaleBarLengthTA = scaleBarLengthTA*sbVector;        % VECTOR
    else
        scaleBarLengthTA = uniqueScaleBarLengthTA;
        scaleRatioTA = uniqueScaleRatioTA;
    end
    
elseif strcmp(plotType, 'split+') || strcmp(plotType, 'split-')

    if ~exist('uniqueScaleRatioTA','var')
        scaleRatioTA = 2e2;                            % 2e3 for 2h average; 3e3 for 4h; 4e3 (or 5e3) for 18h
%         scaleRatioTA = scaleRatioTA*0.322/scale1D;    % correcting for scale  
        scaleBarLengthTA = 2e-1;                       % sets scale bar lengths in the declared uits. 5e-2 for 2h average; 2e-2 for 18h 
        
        srVector =       [ 1   1   1   3    1   2   1   1   1    1    1   1     1       1      1       1       1];
        sbVector =       [ 1   1   1  1/3   1  1/2  1   1   1    1    1   1     1       1      1       1       1];
%      % MCatList =      {{'G';'S';'R';'Ds';'D';'A';'N';'F';'J';'Jb';'DM';'EU';'EGstar';'EPSI';'PhiU';'Ustar';'PhiUstar'}}

        scaleRatioTA = num2cell(scaleRatioTA*srVector);  % CELL ARRAY
        scaleBarLengthTA = scaleBarLengthTA*sbVector;    % VECTOR
        
    else
        nQsTA = 17;                                                     % number of elements in srVector
        scaleRatioTA =  num2cell(repmat(uniqueScaleRatioTA,1,nQsTA));
        scaleBarLengthTA = repmat(uniqueScaleBarLengthTA,1,nQsTA);
%         scaleBarLengthTA = uniqueScaleBarLengthTA;
%         scaleRatioTA = uniqueScaleRatioTA;
    end
end
%-----------------------------------------------------------------------------------------------------------------------


%% STPE Parameters %%

% main parameters:
ABICminMethod = 'fminbnd';              % "fminbnd", "manual" or "forced" (6.6)
muAccuracy = 1e-1;                      % USUALLY 1e-1   ORIGINALLY 1e-6!!
muForced = 1;                           % only relevant when "forced" is chosen for "ABICminMethod"
sMshift = 1;                           % ONLY relevant when "manual" is chosen. Allows shifting of initial sM domain when ABIC(sM(5)) is found to be the minimum. Starts over initial iteration
                                        % over sM values by putting sM(5) at CENTER of new sM domain, keeping initial sM spacing between values.
qrMethod = 'qr';                        % can be either 'qr' (Matlab qr) or 'spqr' (Tim Davis SPQR)
                                        % NB: 'qr' seems to better exploit parallelism
scaleFactorSTPE = 1.0;                 % in micrometer/pixel

%%% display parameters:   
% A/D related:
displayApoptoticCells = false;          % to display apoptotic cells (6.6). MSM MUST HAVE BEEN RUN TO DISPLAY A/D CELLS!!
tSwitch = 1;                            % time (in hours) switch for A/D cells to go from grey to black (6.6)
% P related
makePimage = true;
edgeWidthP = 0.2;                       % width of cell edges in P maps (usually 0.2) 
% rangeP = [];                          % if empty, colorbar will be defined cell Pmin Pmax in image, if not use provided P range
% rangeP = [-0.015 0.020];              % if empty, colorbar will be defined cell Pmin Pmax in image, if not use provided P range
rangeP = [-0.08 0.1];                  % if empty, colorbar will be defined cell Pmin Pmax in image, if not use provided P range
% T related
makeTimage = true;
edgeWidthT = 0.8;                       % width of cell edges in T maps (usually 0.8)  
% rangeT = [];                          % if empty, colorbar will be defined cell Tmin Tmax in image, if not use provided T range% to display mu and ABIC
rangeT = [0.12 1.8];                 % if empty, colorbar will be defined cell Tmin Tmax in image, if not use provided T range
% rangeT = [0.5 1.5];                     % if empty, colorbar will be defined cell Tmin Tmax in image, if not use provided T range


%% MSM parameters %%

nVerticesMin = 3;         % minimal number of vertices used to rescue unmatched Shuji cell numbers
% display parameters:
displayMSM = false;         % if true, will save an image pointing out unmatched Shuji vertices
highlightMRNs = [];        % list of Matlab relative cell numbers to be displayed in magenta.
highlightSRNs = [];        % list of Shuji relative cell numbers to be displayed in magenta. NB: translated Matlab number will be displayed
circleSize = 5;            % size of circles pointing unmatched vertices


%% SM parameters %%

makePlotsSM = false;                                % to generate plots right after computation (6.6)
% display parameters:
plotTensorsSM = {{'S' 'SP' 'ST' 'P'}};                              % tensors to plot: leave empty or 'none', 'all', or 'S' (total stress), 'SP' (pressure part), 'ST' (tension part). NB: use brackets {...} 
killMeanTraceSM =  [  1     1     1      1   ];     % will set average compartment trace to 0 in the plots (mean isotropic part = 0). Choose this when tensors are known up to an additive constant scaling and scale bars:
% contributions       S    SP     ST     P

if ~exist('uniqueScaleRatioSM','var') % 6.3
    % Values for all contributions (S, SP, ST, P IN THIS ORDER):
    scaleRatioSM =     [ 3e3   3e3   3e3   3e3 ];      % CELL ARRAY: sets ratio setting size of ellipses or CD_colors_AOSbars in tensor representation for M,I.
    scaleBarLengthSM = [ 0.02  0.02  0.02  0.02 ];     % VECTOR: scale bar lengths for each contribution
    % contributions       S    SP     ST     P
    AsrVector =        [  1     1     1      1 ];
    IsrVector =        [  1     1     1      1 ];
    %-------------------------------------------------------------------
    
    AscaleRatioSM = scaleRatioSM.*AsrVector;
    IscaleRatioSM = scaleRatioSM.*IsrVector;
    scaleRatioSM = num2cell([IscaleRatioSM; AscaleRatioSM],1); % NB: scaleRatio_AOS MUST BE A CELL ARRAY!!
else
    scaleBarLengthSM = uniqueScaleBarLengthSM;
    scaleRatioSM = uniqueScaleRatioSM;
end


%% Call to "SAP" (8.4) %%

SAP



"""
    return content


def generate_animal_config(
    animal,
    start,
    end,
    n_digits,
    yml="",
    xFactor="",
    yFactor="",
    ox="",
    oy="",
    frame=71,
    temperature=29,
    input_folder="",
):
    """
    Generate the content for an animal configuration file.

    Parameters
    ----------
    animal : str
        Name of the animal.
    start : int
        Starting frame number.
    end : int
        Ending frame number.
    n_digits : int
        Number of digits used for naming raw images.
    yml : str, optional
        Y midline value in pixels (empty if unknown), by default "".
    xFactor : str, optional
        X scaling factor, by default "".
    yFactor : str, optional
        Y scaling factor, by default "".
    ox : str, optional
        X coordinate of the upper left corner, by default "".
    oy : str, optional
        Y coordinate of the upper left corner, by default "".
    frame : int, optional
        Frame number corresponding to time reference, by default 71.
    temperature : int, optional
        Temperature at which development was filmed, by default 29.

    Returns
    -------
    str
        Content of the animal configuration file.
    """

    content = f"""%% Frames to process %%

    startFrame = {start};       % starts @ 1        
    finalFrame = {end};       % ends @ 177

    %% Path to raw images %%

    pathFolderRaw = '{input_folder}/{animal}';
    filenameRaw = {{'{animal}_'}};                  % can be multiple: {{'pten_myo_' ; 'pten_baz_' ; ...}}. NB: PIV will use FIRST listed
    signalName = {{'Cad'}};                       % "Cad", "Myo", "Mud"... (start with capital, names must be used consistently between animals)
    nDigits = {n_digits};                                % number of digits that WAS used for naming RAW IMAGES.
    imageFormatRaw = 'tif';                     % image extension

    %Cells below MUST BE changed/actualised


    %% Synchronization & Scale %%

    halfNotum = 'r';                            % Chose between 'l' (left) 'r' (right) and 'b' 'both'
    frameRef = {frame};                              % frame # corresponding to "timeRef" determined by "TimeRegistration"              
    timeRef = '20h15';                          % "timeRef" ('HH f:MM' or decimal) corresponding to "frameRef" above     18h35 : ¾ of the patches rotation peak    20h15 : ¾ of the cellular divisions peak    25h58 : ¾ of the cellular migration peak

    dt = 5;                                     % time IN MINUTES between two frames
    temperature = {temperature};                           % temperature (25 or 29C) at which development was filmed
    yMid = [{yml}];                                 % y of midline IN PIXELS (leave empty [] if unknown)
    scale1D = 0.161;                            % Length of one pixel IN MICRONS (if 1 pixel is 0.1 um enter 0.1) 
    %Bin 1: 0.161, Bin 2: 0.322;

    %% Box/Grid specifications (PIV, CPT, AOS, TA, SM) %%

    xFactor = {xFactor};                                % X scaling factor from "RescaleAnimals". Animals LONGER than archetype: xFactor > 1
    yFactor = {yFactor};

    boxSize = [40 40]/scale1D  ./ [xFactor yFactor];  	% grid compartment size IN PIXELS [WIDTH HEIGHT]. One value => square grid
    xyStart = [{ox} {oy}];                               % xy coordinates (Upper Left Corner)of FIRST compartment. If empty, starts at image center.
    gridSize = [];                                      % number of compartments [ny nx]. If empty grid fills up image.


    %% Path to clone Mask %% 

    % cloneMaskFrame = 9;                    % frame number corresponding to clone mask
    % cloneName = 'COMP';                         % name to give to clone ("a-act", "fat"...)
    % path2cloneMask = 'D:\BigMovies\BIGwt2\Masks\COMP_mask_BIGwt2_0009.png'; 

    %% Scale Bar & Display %%

    scaleBarLength = 50;                    % scale bar length in microns
    scaleBarWidth = 3;                      % scale bar width (in PIXELS). Used 3 for BIG
    xyOffset = [30 70];                     % scale bar offset @ bottom right of image IN PIXELS ([30 30] for Potts)
    colorBarXYWH = [0.75 0.025 0.15 0.02];    % [left, bottom, width, height] in figure units
    imageFading = 0.7;                      % fading of background image for tensor maps (0.7 for eLife article)
    fontSizeInfo = 18;                      % 27 TRBL8(res 200), 35 BIG_X,TRBL9,TRBL4(res 150), 55 TRBL7(res 100), 20 BIG (res 300), 40 JESUS(res 200), but 27 (res300) for cad4
    imageResolution = 125;                  % 300 used for formalism article, 200 for Potts CppTD images, between 300 and 150 for CppTD images

    %% "SAP_parameters" call %%

    Animal = mfilename;
    Animal = Animal(10:end);
    SAP_parameters

    """
    return content
