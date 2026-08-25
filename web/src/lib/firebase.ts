import { initializeApp, getApps } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Firebase config from google-services.json / Firebase console
const firebaseConfig = {
  apiKey: 'AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA',
  authDomain: 'orthofinixai.firebaseapp.com',
  projectId: 'orthofinixai',
  storageBucket: 'orthofinixai.firebasestorage.app',
  messagingSenderId: '1095608848739',
  appId: '1:1095608848739:web:orthofinixai',
};

// Initialize Firebase only once
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
console.log("WEB FIREBASE CONFIG -> projectId:", firebaseConfig.projectId, "appId:", firebaseConfig.appId);
export const firebaseAuth = getAuth(app);
export const db = getFirestore(app);
export default app;

