//
//  MasterViewController.swift
//  Soundboard
//
//  Created by Dominic Henze on 24.09.19.
//  Copyright © 2019 Dominic Henze. All rights reserved.
//

import UIKit

class MasterViewController: UITableViewController {
    
    struct Constants {
        static let showDetailSegue = "showDetail"
        static let cellIdentifier = "Cell"
        
        static let TitleTextSize: CGFloat = 25
        static let CellTitleTextSize: CGFloat = 20
        static let CellDetailTextSize: CGFloat = 15
    }

    var detailViewController: DetailViewController? = nil

    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.title = Config.Master.Text.barText
        
        self.navigationController?.navigationBar.barTintColor = Config.Master.Color.barColor
        self.navigationController?.navigationBar.titleTextAttributes = [NSAttributedString.Key.foregroundColor: Config.Master.Color.barTextColor, NSAttributedString.Key.font: UIFont.boldSystemFont(ofSize: Constants.TitleTextSize)]
        
        self.tableView.backgroundColor = Config.Master.Color.backgroundColor
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        
        self.tableView.selectRow(at: IndexPath(row: 0, section: 0), animated: false, scrollPosition: .top)
        self.performSegue(withIdentifier: Constants.showDetailSegue, sender: nil)
    }

    // MARK: - Segues
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == Constants.showDetailSegue {
            if let indexPath = tableView.indexPathForSelectedRow {
                let object = SoundData.shared.mockData[indexPath.row]
                let controller = (segue.destination as! UINavigationController).topViewController as! DetailViewController
                
                controller.detailItem = object
                controller.navigationItem.leftBarButtonItem = splitViewController?.displayModeButtonItem
                controller.navigationItem.leftItemsSupplementBackButton = true
                
                detailViewController = controller
            }
        }
    }

    // MARK: - Table View
    override func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return SoundData.shared.mockData.count
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: Constants.cellIdentifier, for: indexPath)
        let soundObject = SoundData.shared.mockData[indexPath.row]
        let selectionBackgroundView = UIView()
        
        selectionBackgroundView.backgroundColor = Config.Master.Color.cellHighlightColor
        
        cell.selectedBackgroundView = selectionBackgroundView
        cell.textLabel?.text = soundObject.name
        cell.textLabel?.textColor = Config.Master.Color.cellTextColor
        cell.textLabel?.font = UIFont.systemFont(ofSize: Constants.CellTitleTextSize, weight: .bold)
        cell.detailTextLabel?.text = soundObject.artist
        cell.detailTextLabel?.textColor = Config.Master.Color.cellDetailTextColor
        cell.detailTextLabel?.font = UIFont.systemFont(ofSize: Constants.CellDetailTextSize, weight: .regular)
        cell.backgroundColor = Config.Master.Color.cellBackgroundColor
        cell.imageView?.image = soundObject.image
        cell.imageView?.tintColor = Config.Master.Color.cellBackupIcon
        
        return cell
    }
}
