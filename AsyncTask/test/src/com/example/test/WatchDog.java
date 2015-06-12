package com.example.test;

import android.content.Context;
import android.util.Log;

import com.android.uiautomator.core.UiCollection;
import com.android.uiautomator.core.UiDevice;
import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.core.UiWatcher;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class WatchDog extends UiAutomatorTestCase {

	
	private static final String LOG_TAG = "WatcherDemoEx1";
	private static final String MYOKCANCELDIALOGWATCHER_STRING = "OkCancelDialogWatcher";
	private Context context;

		
	public class uiWatcherDemo extends UiAutomatorTestCase {

		  private static final String NOINTERNET_STRING = "InternetWatcher";

		  public void testWatcherDemoTestExample() throws UiObjectNotFoundException {

		      // Define watcher and register //
		      UiWatcher internetWatcher = new UiWatcher() {
		          @Override
		          public boolean checkForCondition() {
		              UiObject noConnObj = new UiObject(new UiSelector().text("No connection"));
		              if(noConnObj.exists()) {
		                  UiObject retryButton = new UiObject(new UiSelector().className("android.widget.Button").text("Retry"));
		                  try {
		                      retryButton.click();
		                      try { Thread.sleep(3000L); } catch(Exception e) {}
		                      getUiDevice().pressHome();
		                  } catch (UiObjectNotFoundException e) {
		                      e.printStackTrace();
		                  }
		              }
		              return false;
		          }
		      };
		      getUiDevice().registerWatcher(NOINTERNET_STRING, internetWatcher);
		      getUiDevice().runWatchers();

		      // app test code //
		      getUiDevice().pressHome();
		      UiObject allAppsButton = new UiObject(new   UiSelector().description("Apps"));
		      allAppsButton.clickAndWaitForNewWindow();
//		      UiObject appsTab = new UiObject(new UiSelector().description("Shop"));
//		      appsTab.clickAndWaitForNewWindow();
		      UiObject contact = new UiObject(new UiSelector().text("Contacts"));
		      contact.click();
		  }
		}

}



