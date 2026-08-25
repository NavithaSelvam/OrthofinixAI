import React, { createContext, useContext, useState } from 'react';

interface SharedCaseContextType {
  patientName: string;
  dob: string;
  gender: string;
  clinicalPhotos: (File | null)[];
  opgPhoto: File | null;
  setPatientName: (name: string) => void;
  setDob: (dob: string) => void;
  setGender: (gender: string) => void;
  setClinicalPhoto: (index: number, file: File | null) => void;
  setOpgPhoto: (file: File | null) => void;
  reset: () => void;
}

const SharedCaseContext = createContext<SharedCaseContextType | undefined>(undefined);

export const SharedCaseProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [patientName, setPatientNameState] = useState('');
  const [dob, setDobState] = useState('');
  const [gender, setGenderState] = useState('Male');
  const [clinicalPhotos, setClinicalPhotos] = useState<(File | null)[]>(Array(9).fill(null));
  const [opgPhoto, setOpgPhotoState] = useState<File | null>(null);

  const setPatientName = (name: string) => setPatientNameState(name);
  const setDob = (d: string) => setDobState(d);
  const setGender = (g: string) => setGenderState(g);
  
  const setClinicalPhoto = (index: number, file: File | null) => {
    setClinicalPhotos((prev) => {
      const next = [...prev];
      next[index] = file;
      return next;
    });
  };

  const setOpgPhoto = (file: File | null) => setOpgPhotoState(file);

  const reset = () => {
    setPatientNameState('');
    setDobState('');
    setGenderState('Male');
    setClinicalPhotos(Array(9).fill(null));
    setOpgPhotoState(null);
  };

  return (
    <SharedCaseContext.Provider
      value={{
        patientName,
        dob,
        gender,
        clinicalPhotos,
        opgPhoto,
        setPatientName,
        setDob,
        setGender,
        setClinicalPhoto,
        setOpgPhoto,
        reset,
      }}
    >
      {children}
    </SharedCaseContext.Provider>
  );
};

export const useSharedCase = () => {
  const context = useContext(SharedCaseContext);
  if (!context) {
    throw new Error('useSharedCase must be used within a SharedCaseProvider');
  }
  return context;
};
