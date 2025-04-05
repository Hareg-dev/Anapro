#include <iostream>
#include <vector>
#include <fstream>
#include <algorithm>  // For sorting

using namespace std;

// Class representing a Gym Member
class Member {
public:
    int id;
    string name;
    int age;
    string membershipType;
    bool feesPaid;

    Member(int _id, string _name, int _age, string _membershipType, bool _feesPaid) {
        id = _id;
        name = _name;
        age = _age;
        membershipType = _membershipType;
        feesPaid = _feesPaid;
    }
};

// Gym Management System class
class GymManagement {
private:
    vector<Member> members;

public:
    // Add a new member
    void addMember(int id, string name, int age, string membershipType, bool feesPaid) {
        members.push_back(Member(id, name, age, membershipType, feesPaid));
        cout << "Member added successfully!\n";
    }

    // Display all members
    void displayMembers() {
        if (members.empty()) {
            cout << "No members found!\n";
            return;
        }
        cout << "\n--- Gym Members List ---\n";
        for (const auto &m : members) {
            cout << "ID: " << m.id << ", Name: " << m.name
                 << ", Age: " << m.age << ", Membership: " << m.membershipType
                 << ", Fees Paid: " << (m.feesPaid ? "Yes" : "No") << "\n";
        }
    }

    // Linear Search for a member by name
    void linearSearch(string searchName) {
        bool found = false;
        for (const auto &m : members) {
            if (m.name == searchName) {
                cout << "Member found - ID: " << m.id << ", Name: " << m.name << "\n";
                found = true;
                break;
            }
        }
        if (!found) cout << "Member not found!\n";
    }

    // Binary Search (requires sorted members)
    int binarySearch(string searchName) {
        int left = 0, right = members.size() - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (members[mid].name == searchName) return mid;
            else if (members[mid].name < searchName) left = mid + 1;
            else right = mid - 1;
        }
        return -1;
    }

    // Sorting Algorithms
    void bubbleSort() {
        int n = members.size();
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (members[j].name > members[j + 1].name) {
                    swap(members[j], members[j + 1]);
                }
            }
        }
        cout << "Sorted using Bubble Sort!\n";
    }

    void selectionSort() {
        int n = members.size();
        for (int i = 0; i < n - 1; i++) {
            int minIndex = i;
            for (int j = i + 1; j < n; j++) {
                if (members[j].name < members[minIndex].name) {
                    minIndex = j;
                }
            }
            swap(members[i], members[minIndex]);
        }
        cout << "Sorted using Selection Sort!\n";
    }

    void insertionSort() {
        int n = members.size();
        for (int i = 1; i < n; i++) {
            Member key = members[i];
            int j = i - 1;
            while (j >= 0 && members[j].name > key.name) {
                members[j + 1] = members[j];
                j--;
            }
            members[j + 1] = key;
        }
        cout << "Sorted using Insertion Sort!\n";
    }

    void quickSort(int low, int high) {
        if (low < high) {
            int pi = partition(low, high);
            quickSort(low, pi - 1);
            quickSort(pi + 1, high);
        }
    }

    int partition(int low, int high) {
        string pivot = members[high].name;
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (members[j].name < pivot) {
                i++;
                swap(members[i], members[j]);
            }
        }
        swap(members[i + 1], members[high]);
        return i + 1;
    }

    void sortUsingQuickSort() {
        quickSort(0, members.size() - 1);
        cout << "Sorted using Quick Sort!\n";
    }

    // Save data to file
    void saveToFile() {
        ofstream outFile("members.txt");
        for (const auto &m : members) {
            outFile << m.id << " " << m.name << " " << m.age << " " << m.membershipType << " " << m.feesPaid << "\n";
        }
        outFile.close();
        cout << "Data saved to file!\n";
    }

    // Load data from file
    void loadFromFile() {
        ifstream inFile("members.txt");
        if (!inFile) {
            cout << "No saved data found!\n";
            return;
        }

        members.clear();
        int id, age;
        string name, membershipType;
        bool feesPaid;
        while (inFile >> id >> name >> age >> membershipType >> feesPaid) {
            members.push_back(Member(id, name, age, membershipType, feesPaid));
        }
        inFile.close();
        cout << "Data loaded from file!\n";
    }
};

// Main function
int main() {
    GymManagement gym;
    gym.loadFromFile();

    int choice;
    do {
        cout << "\n--- Gym Management System ---\n";
        cout << "1. Add Member\n2. Display Members\n3. Search Member (Linear Search)\n";
        cout << "4. Sort Members (Bubble, Selection, Insertion, Quick Sort)\n";
        cout << "5. Search Member (Binary Search)\n6. Save & Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;

        if (choice == 1) {
            int id, age;
            string name, membershipType;
            bool feesPaid;
            cout << "Enter ID, Name, Age, Membership Type, Fees Paid (1 for Yes, 0 for No): ";
            cin >> id >> name >> age >> membershipType >> feesPaid;
            gym.addMember(id, name, age, membershipType, feesPaid);
        } 
        else if (choice == 2) {
            gym.displayMembers();
        } 
        else if (choice == 3) {
            string searchName;
            cout << "Enter name to search: ";
            cin >> searchName;
            gym.linearSearch(searchName);
        } 
        else if (choice == 4) {
            gym.sortUsingQuickSort();  // Efficient sort
        } 
        else if (choice == 5) {
            string searchName;
            cout << "Enter name to search (Binary Search): ";
            cin >> searchName;
            int index = gym.binarySearch(searchName);
            if (index != -1)
                cout << "Member found at index " << index << "!\n";
            else
                cout << "Member not found!\n";
        }
    } while (choice != 6);

    gym.saveToFile();
    cout << "Exiting program...\n";
    return 0;
}