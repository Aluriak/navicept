%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXPANSION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% All available dimensions.
dim(I):- set(I,_).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PROBLEM ENCODING
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Guess one formal concept.
in(I,X):- set(I,X) ; not out(I,X).
out(I,X):- set(I,X) ; not in(I,X).

% All relations must hold.  [n=2]
:- in(1,X) ; in(2,Y) ; not rel(X,Y).

% Concept must exists in all dimensions.
:- dim(I) ; not in(I,_).

% Maximality condition.  [n=2]
exc(1,X):- set(1,X) ; not in(1,X) ; in(2,Y) ; not rel(X,Y).
exc(2,X):- set(2,X) ; not in(2,X) ; in(1,Y) ; not rel(Y,X).
:- out(I,X) ; not exc(I,X).

% Membership constraints.
:- out(I,X) ; required(I,X).
:- in(I,X) ; forbidden(I,X).


#show.
#show in/2.
% #show out/2.
