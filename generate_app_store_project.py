import os

def create_app_store_files():
    # Define clean source directory architecture
    dirs = [
        "AppStoreProject",
        "AppStoreProject/Models",
        "AppStoreProject/Views",
        "AppStoreProject/Services"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Create App Data Model
    model_code = """import Foundation

struct AppItem: Identifiable, Codable {
    let id: UUID
    let title: String
    let subtitle: String
    let version: String
    let ipaURL: URL?
    let iconName: String
}
"""
    with open("AppStoreProject/Models/AppItem.swift", "w") as f:
        f.write(model_code)

    # 2. Create the Complete Application Interface featuring the '+' Button
    view_code = """import SwiftUI
import UniformTypeIdentifiers

struct MainStoreView: View {
    @State private var availableApps: [AppItem] = [
        AppItem(id: UUID(), title: "Roblox", subtitle: "Play Millions of Games", version: "2.640.0", ipaURL: nil, iconName: "gamecontroller"),
        AppItem(id: UUID(), title: "Dr. Driving", subtitle: "Dr. Driving drives you crazy!", version: "1.69", ipaURL: nil, iconName: "car"),
        AppItem(id: UUID(), title: "Combat Master", subtitle: "Fast-Paced ActionFPS", version: "0.12.3", ipaURL: nil, iconName: "shield")
    ]
    @State private var showFilePicker = false

    var body: some View {
        NavigationView {
            List(availableApps) { app in
                HStack(spacing: 16) {
                    Image(systemName: app.iconName)
                        .resizable()
                        .scaledToFit()
                        .frame(width: 40, height: 40)
                        .padding(10)
                        .background(Color(.systemGray5))
                        .cornerRadius(12)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(app.title)
                            .font(.headline)
                        Text(app.subtitle)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Button(action: {
                        print("Triggering on-device signing configuration for: \\(app.title)")
                    }) {
                        Text("GET")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.blue)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 6)
                            .background(Color(.systemGroupedBackground))
                            .cornerRadius(20)
                    }
                }
                .padding(.vertical, 4)
            }
            .navigationTitle("Discover")
            .toolbar {
                // Top-Left Placement for adding custom IPAs
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        showFilePicker = true
                    }) {
                        Image(systemName: "plus")
                            .font(.title2)
                    }
                }
            }
            .sheet(isPresented: $showFilePicker) {
                DocumentPicker(apps: $availableApps)
            }
        }
    }
}

// System Bridge to import local unsigned IPA files into your Custom Store interface
struct DocumentPicker: UIViewControllerRepresentable {
    @Binding var apps: [AppItem]
    
    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [UTType(filenameExtension: "ipa")!])
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIDocumentPickerDelegate {
        var parent: DocumentPicker
        init(_ parent: DocumentPicker) { self.parent = parent }
        
        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let selectedURL = urls.first else { return }
            let fileName = selectedURL.deletingPathExtension().lastPathComponent
            
            // Append the new custom application package to your dashboard layout
            let newApp = AppItem(id: UUID(), title: fileName, subtitle: "Imported Local IPA File", version: "Local", ipaURL: selectedURL, iconName: "doc.badge.plus")
            parent.apps.append(newApp)
        }
    }
}
"""
    with open("AppStoreProject/Views/MainStoreView.swift", "w") as f:
        f.write(view_code)

    # 3. Create entry point
    app_entry = """import SwiftUI
@main
struct AppStoreTarget: App {
    var body: some Scene {
        WindowGroup {
            MainStoreView()
        }
    }
}"""
    with open("AppStoreProject/AppStoreTarget.swift", "w") as f:
        f.write(app_entry)

    # 4. Create the Project Specification file for XcodeGen
    project_yaml = """name: AppStoreProject
options:
  bundleIdPrefix: com.malek
targets:
  AppStoreProject:
    type: application
    platform: iOS
    deploymentTarget: "15.0"
    sources: [AppStoreProject]
"""
    with open("project.yml", "w") as f:
        f.write(project_yaml)

    print("\n[Success] Core structural definitions created!")

if __name__ == "__main__":
    create_app_store_files()
