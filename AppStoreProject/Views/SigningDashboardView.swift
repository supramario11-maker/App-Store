
import SwiftUI

struct SigningDashboardView: View {
    @State private var certificateExpiry = Calendar.current.date(
        byAdding: .day,
        value: 7,
        to: Date()
    ) ?? Date()

    @State private var checkingServers = false
    @State private var serverStatuses: [String: String] = [:]
    @State private var lastChecked: Date?

    // Add real HTTPS health-check URLs for services you trust.
    // Leave a URL empty until you have a real endpoint.
    private let servers: [(name: String, platform: String, url: String)] = [
        ("macOS Signing Service", "macOS", ""),
        ("Windows Signing Service", "Windows", ""),
        ("Linux Cloud Service", "Linux", "")
    ]

    private var daysRemaining: Int {
        Calendar.current.dateComponents(
            [.day],
            from: Date(),
            to: certificateExpiry
        ).day ?? 0
    }

    var body: some View {
        NavigationView {
            List {
                Section("Signing Status") {
                    Label {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Personal signing")
                                .font(.headline)
                            Text("Use a trusted signing tool")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    } icon: {
                        Image(systemName: "checkmark.shield.fill")
                            .foregroundColor(.blue)
                    }

                    Link(
                        "Open SideStore",
                        destination: URL(
                            string: "https://sidestore.io"
                        )!
                    )
                }

                Section("Signing Services") {
                    ForEach(servers, id: \.name) { server in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(server.name)
                                    .font(.headline)
                                Text(server.platform)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }

                            Spacer()

                            Text(
                                serverStatuses[server.name]
                                    ?? "Not checked"
                            )
                            .font(.caption)
                            .foregroundColor(
                                serverStatuses[server.name] == "Online"
                                    ? .green
                                    : .secondary
                            )
                        }
                    }

                    Button {
                        checkServers()
                    } label: {
                        HStack {
                            if checkingServers {
                                ProgressView()
                            } else {
                                Image(systemName: "arrow.clockwise")
                            }

                            Text("Check Configured Services")
                        }
                    }
                    .disabled(checkingServers)

                    if let lastChecked {
                        Text(
                            "Last checked: \(lastChecked.formatted(date: .abbreviated, time: .shortened))"
                        )
                        .font(.caption)
                        .foregroundColor(.secondary)
                    }
                }

                Section("Certificate Expiration") {
                    DatePicker(
                        "Expected expiration",
                        selection: $certificateExpiry,
                        in: Date()...,
                        displayedComponents: .date
                    )

                    HStack {
                        Text("Time remaining")
                        Spacer()
                        Text(
                            daysRemaining >= 0
                                ? "\(daysRemaining) days"
                                : "Expired"
                        )
                        .foregroundColor(
                            daysRemaining <= 2 ? .orange : .primary
                        )
                    }

                    Text(
                        "This is a reminder tracker, not a live reading of your Apple certificate."
                    )
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Signing Dashboard")
        }
    }

    private func checkServers() {
        checkingServers = true

        let configuredServers = servers.filter {
            !$0.url.trimmingCharacters(
                in: .whitespacesAndNewlines
            ).isEmpty
        }

        guard !configuredServers.isEmpty else {
            serverStatuses = Dictionary(
                uniqueKeysWithValues: servers.map {
                    ($0.name, "Not configured")
                }
            )
            checkingServers = false
            lastChecked = Date()
            return
        }

        let group = DispatchGroup()

        for server in configuredServers {
            guard let url = URL(string: server.url),
                  url.scheme == "https" else {
                serverStatuses[server.name] = "Invalid HTTPS URL"
                continue
            }

            group.enter()

            var request = URLRequest(url: url)
            request.httpMethod = "GET"
            request.timeoutInterval = 10

            URLSession.shared.dataTask(with: request) {
                _, response, error in

                let status: String

                if let error {
                    status = "Unavailable"
                    _ = error
                } else if let response = response as? HTTPURLResponse,
                          (200...299).contains(response.statusCode) {
                    status = "Online"
                } else {
                    status = "Unavailable"
                }

                DispatchQueue.main.async {
                    serverStatuses[server.name] = status
                }

                group.leave()
            }.resume()
        }

        group.notify(queue: .main) {
            for server in servers where
                server.url.trimmingCharacters(
                    in: .whitespacesAndNewlines
                ).isEmpty {
                serverStatuses[server.name] = "Not configured"
            }

            checkingServers = false
            lastChecked = Date()
        }
    }
}

#Preview {
    SigningDashboardView()
}
