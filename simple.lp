%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXPANSION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% All available dimensions.
dim(I):- set(I,_).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PROBLEM ENCODING
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Guess one formal concept.
in(K,X):- set(K,X) ; not out(K,X).

% The following lines are just examples of how to handle the 2 dimensions case.
% External programs needs to inject there own versions of these lines if they want
% this encoding to work properly.
% See nconcept.py module.
% out(1,X):- set(1,X) ; in(2,Y) ; not rel(X,Y).
% out(2,X):- set(2,X) ; in(1,Y) ; not rel(Y,X).

% Concept must exists in all dimensions.
:- not in(K,_) ; dim(K).

% Membership constraints.
:- out(I,X) ; required(I,X).
:- in(I,X) ; forbidden(I,X).


#show.
#show in/2.
