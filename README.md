# GuardianData :guardsman:

Data sharing is essential for collaboration, but it also presents privacy risks when sensitive information is involved. In this project, students can develop a privacy-preserving data sharing system using free and open-source tools such as Python, ZeroMQ, and Homomorphic Encryption. They can start by designing a system that encrypts data before sharing it and uses homomorphic encryption to perform computations on encrypted data. The practical component of this project could involve testing the system's security features and creating a report that outlines the results.
 
The Privacy-Preserving Data Sharing System Project involves developing a system that enables secure sharing of sensitive data while preserving the privacy of the data. The system should allow users to share encrypted data with other users, perform computations on encrypted data, and receive the results without revealing the data to unauthorized parties. This project can be implemented using free and open-source tools such as Python, ZeroMQ, and Homomorphic Encryption.

The practical component of this project involves developing the privacy-preserving data sharing system and testing its functionality and performance. The following are the steps involved in the practical component of this project:

#### Generating Public and Private Keys
In this step, students will generate public and private keys using a cryptographic library such as PyCryptodome. These keys will be used to encrypt and decrypt data.

#### Encrypting the Data
Students will use the generated public key to encrypt the data to be shared. They can use a cryptographic library such as PyCryptodome to perform the encryption.

#### Sharing the Encrypted Data
The encrypted data can be shared using a message queue system such as ZeroMQ. Students will need to configure ZeroMQ to enable secure communication between users.

#### Performing Computations on Encrypted Data
Homomorphic encryption enables computations to be performed on encrypted data without decrypting it. Students can use a homomorphic encryption library such as Pyfhel to perform computations on the encrypted data.

#### Receiving Results
The results of the computations can be sent back to the user who requested them using the same message queue system used to share the encrypted data. The results will be encrypted and can be decrypted using the private key.

#### Testing the System
Once the privacy-preserving data sharing system is developed, students can test its functionality and performance. They can use sample data to test the system's ability to securely share data, perform computations on encrypted data, and receive results without revealing the data to unauthorized parties.
