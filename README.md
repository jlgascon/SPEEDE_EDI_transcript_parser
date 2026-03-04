
# EDI Transcript Parser & Classifier

## Description

This Python script automates the parsing of raw SPEEDE/EDI transcript text files. It uses regular expressions to isolate specific data blocks, extract critical student metadata, and classify the overall status of the transcript based on institutional grading flags and degree completion markers.

## Features

> Block-Restricted Parsing: Safely extracts the Agency's Student Number exclusively from the Student Information header to prevent capturing irrelevant numerical data.

> Status Classification: Evaluates academic records to flag transcripts as Complete, In-Progress, or Incomplete / Withdrawn by detecting specific grading strings (e.g., INP, --) and degree indicators.

## Output

The script will print a markdown-formatted table to the console containing:

   - Student Name
   - Agency's Student Number
   - Sent by Institution
   - Transcript Status
